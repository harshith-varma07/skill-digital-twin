import { useMemo, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { learningService } from '../services/api'
import { AcademicCapIcon, PlayCircleIcon, CheckCircleIcon } from '@heroicons/react/24/outline'

interface RoadmapModule {
  id: number
  title: string
  description?: string
  due_date?: string
  completion_percentage: number
  status: 'not_started' | 'in_progress' | 'completed'
  resources: Array<{
    id: number
    title: string
    type: 'video' | 'article' | 'course'
    url: string
    progress: number
  }>
}

interface Roadmap {
  id: number
  title: string
  description?: string
  progress_percentage: number
  is_active: boolean
  modules: RoadmapModule[]
}

export default function LearningRoadmap() {
  const queryClient = useQueryClient()
  const [selectedRoadmapId, setSelectedRoadmapId] = useState<number | null>(null)

  const { data: roadmaps, isLoading } = useQuery({
    queryKey: ['learning-roadmaps', 'all'],
    queryFn: async () => {
      const response = await learningService.getRoadmaps()
      return response.data as Roadmap[]
    },
  })

  const selectedRoadmap = useMemo(() => {
    if (!roadmaps?.length) return null
    if (selectedRoadmapId) return roadmaps.find(r => r.id === selectedRoadmapId) || roadmaps[0]
    return roadmaps[0]
  }, [roadmaps, selectedRoadmapId])

  const updateModuleProgress = useMutation({
    mutationFn: async ({ moduleId, progress }: { moduleId: number; progress: number }) => {
      return learningService.updateResourceProgress(moduleId, progress)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning-roadmaps'] })
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (!roadmaps?.length) {
    return (
      <div className="text-center py-16 bg-white rounded-xl shadow-sm border border-gray-100">
        <AcademicCapIcon className="h-12 w-12 text-gray-300 mx-auto" />
        <p className="mt-2 text-gray-600">No learning roadmaps yet</p>
        <p className="text-sm text-gray-500">Generate one based on your skill gaps</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Learning Roadmaps</h1>
          <p className="text-gray-600">Track your learning journey and progress</p>
        </div>
      </div>

      {/* Roadmap selector */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-sm text-gray-600">Active roadmaps:</span>
          <div className="flex flex-wrap gap-2">
            {roadmaps.map(r => (
              <button
                key={r.id}
                onClick={() => setSelectedRoadmapId(r.id)}
                className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
                  selectedRoadmap?.id === r.id
                    ? 'bg-primary-600 text-white border-primary-600'
                    : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
                }`}
              >
                {r.title}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Selected Roadmap */}
      {selectedRoadmap && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">{selectedRoadmap.title}</h2>
                {selectedRoadmap.description && (
                  <p className="text-gray-600">{selectedRoadmap.description}</p>
                )}
              </div>
              <div className="w-64">
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-500">Overall Progress</span>
                  <span className="font-medium text-gray-700">{selectedRoadmap.progress_percentage}%</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${selectedRoadmap.progress_percentage}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Modules */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {selectedRoadmap.modules.map((m) => (
              <div key={m.id} className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{m.title}</h3>
                    {m.description && (
                      <p className="text-sm text-gray-600 mt-1">{m.description}</p>
                    )}
                  </div>
                  <span
                    className={`px-2 py-1 text-xs rounded-full font-medium ${
                      m.status === 'completed'
                        ? 'bg-green-100 text-green-700'
                        : m.status === 'in_progress'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {m.status.replace('_', ' ')}
                  </span>
                </div>

                <div className="mt-4">
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-500">Completion</span>
                    <span className="font-medium text-gray-700">{m.completion_percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${m.completion_percentage}%` }}
                    />
                  </div>
                </div>

                {/* Resources */}
                <div className="mt-4 space-y-3">
                  {m.resources.map(r => (
                    <a
                      key={r.id}
                      href={r.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className="p-2 rounded-lg bg-primary-50 text-primary-600">
                          {r.type === 'video' ? <PlayCircleIcon className="h-5 w-5" /> : <AcademicCapIcon className="h-5 w-5" />}
                        </span>
                        <div>
                          <p className="text-sm font-medium text-gray-900">{r.title}</p>
                          <p className="text-xs text-gray-500 capitalize">{r.type}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-24 bg-gray-100 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${r.progress}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-500">{r.progress}%</span>
                      </div>
                    </a>
                  ))}
                </div>

                <div className="mt-4 flex items-center justify-end gap-2">
                  {m.status !== 'completed' && (
                    <button
                      onClick={() => updateModuleProgress.mutate({ moduleId: m.id, progress: Math.min(100, m.completion_percentage + 10) })}
                      className="inline-flex items-center gap-2 px-3 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                    >
                      <CheckCircleIcon className="h-4 w-4" /> Mark +10%
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
