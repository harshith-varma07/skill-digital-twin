import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { assessmentService } from '../services/api'
import { ChartBarIcon, QuestionMarkCircleIcon, PlayIcon } from '@heroicons/react/24/outline'

interface Assessment {
  id: number
  title: string
  description?: string
  created_at: string
  status?: 'not_started' | 'in_progress' | 'completed'
}

interface Question {
  id: number
  question_text: string
  options: string[]
  correct_answer?: string
}

export default function Assessments() {
  const queryClient = useQueryClient()
  const [activeAssessment, setActiveAssessment] = useState<Assessment | null>(null)
  const [responses, setResponses] = useState<Record<number, string>>({})
  
  const { data: assessments, isLoading } = useQuery({
    queryKey: ['assessments'],
    queryFn: async () => {
      const response = await assessmentService.getAssessments({ limit: 10 })
      return response.data as Assessment[]
    },
  })

  const { data: questions } = useQuery({
    queryKey: ['assessment', activeAssessment?.id],
    enabled: !!activeAssessment,
    queryFn: async () => {
      if (!activeAssessment) return []
      const response = await assessmentService.getAssessment(activeAssessment.id)
      return (response.data?.questions || []) as Question[]
    },
  })

  const start = useMutation({
    mutationFn: async (id: number) => assessmentService.startAssessment(id),
    onSuccess: (_, id) => {
      const a = assessments?.find(a => a.id === id)
      if (a) setActiveAssessment(a)
    },
  })

  const submit = useMutation({
    mutationFn: async (id: number) => {
      const formatted = Object.entries(responses).map(([question_id, answer]) => ({ question_id: Number(question_id), answer }))
      return assessmentService.submitAssessment(id, formatted)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessments'] })
      setActiveAssessment(null)
      setResponses({})
    },
  })

  const setAnswer = (questionId: number, answer: string) => {
    setResponses(prev => ({ ...prev, [questionId]: answer }))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Assessments</h1>
          <p className="text-gray-600">Take diagnostics and practice questions</p>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full" />
        </div>
      ) : activeAssessment ? (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">{activeAssessment.title}</h2>
          </div>

          <div className="space-y-6">
            {questions?.map((q, idx) => (
              <div key={q.id} className="border border-gray-100 rounded-lg p-4">
                <p className="font-medium text-gray-900">
                  Q{idx + 1}. {q.question_text}
                </p>
                <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {q.options.map(opt => (
                    <label key={opt} className={`flex items-center gap-2 p-2 rounded-lg border cursor-pointer ${responses[q.id] === opt ? 'border-primary-300 bg-primary-50' : 'border-gray-200 hover:bg-gray-50'}`}>
                      <input
                        type="radio"
                        name={`q-${q.id}`}
                        checked={responses[q.id] === opt}
                        onChange={() => setAnswer(q.id, opt)}
                      />
                      <span className="text-sm text-gray-700">{opt}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}

            <div className="flex justify-end">
              <button
                onClick={() => activeAssessment && submit.mutate(activeAssessment.id)}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Submit Assessment
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {assessments?.map((a) => (
            <div key={a.id} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{a.title}</h3>
                  {a.description && (
                    <p className="text-sm text-gray-600 mt-1">{a.description}</p>
                  )}
                </div>
                <span className="p-2 bg-primary-50 text-primary-600 rounded-lg">
                  <QuestionMarkCircleIcon className="h-5 w-5" />
                </span>
              </div>
              <div className="mt-4">
                <button
                  onClick={() => start.mutate(a.id)}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  <PlayIcon className="h-4 w-4" /> Start Assessment
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
