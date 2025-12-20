import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { careerService } from '../services/api'
import { BriefcaseIcon, CheckCircleIcon } from '@heroicons/react/24/outline'

interface Role {
  id: number
  title: string
  level: string
  description?: string
}

interface AlignmentResult {
  role_id: number
  readiness_percentage: number
  matching_skills: Array<{ skill_id: number; skill_name: string; weight: number }>
  missing_skills: Array<{ skill_id: number; skill_name: string; weight: number }>
}

export default function CareerAlignment() {
  const [selectedRole, setSelectedRole] = useState<number | ''>('')
  const queryClient = useQueryClient()

  const { data: roles } = useQuery({
    queryKey: ['career-roles'],
    queryFn: async () => {
      const response = await careerService.getRoles()
      return response.data as Role[]
    },
  })

  const { data: alignment, refetch, isFetching } = useQuery({
    queryKey: ['career-alignment', selectedRole],
    enabled: false,
    queryFn: async () => {
      const id = typeof selectedRole === 'number' ? selectedRole : roles?.[0]?.id
      if (!id) return null
      const response = await careerService.getAlignment(id)
      return response.data as AlignmentResult
    },
  })

  const setTarget = useMutation({
    mutationFn: async (roleId: number) => careerService.setTargetRole(roleId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['career-roles'] }),
  })

  const handleAnalyze = () => refetch()

  const getBadgeClass = (value: number) => {
    if (value >= 80) return 'bg-green-100 text-green-700'
    if (value >= 60) return 'bg-blue-100 text-blue-700'
    if (value >= 40) return 'bg-yellow-100 text-yellow-700'
    return 'bg-red-100 text-red-700'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Career Alignment</h1>
          <p className="text-gray-600">See how your skills match target roles</p>
        </div>
      </div>

      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Select Role</label>
            <div className="relative">
              <BriefcaseIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value ? parseInt(e.target.value) : '')}
                className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">Select a role</option>
                {roles?.map(role => (
                  <option key={role.id} value={role.id}>
                    {role.title} ({role.level})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex items-end">
            <button
              onClick={handleAnalyze}
              className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Analyze Alignment
            </button>
          </div>

          <div className="flex items-end">
            <button
              disabled={typeof selectedRole !== 'number'}
              onClick={() => typeof selectedRole === 'number' && setTarget.mutate(selectedRole)}
              className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <CheckCircleIcon className="h-5 w-5 inline mr-2" /> Set as Target
            </button>
          </div>
        </div>
      </div>

      {isFetching ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full" />
        </div>
      ) : alignment ? (
        <div className="space-y-6">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Readiness Percentage</p>
                <p className="text-3xl font-bold text-gray-900">{alignment.readiness_percentage.toFixed(0)}%</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getBadgeClass(alignment.readiness_percentage)}`}>
                {alignment.readiness_percentage >= 70 ? 'Strong Fit' : alignment.readiness_percentage >= 40 ? 'Moderate Fit' : 'Developing'}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Matching skills */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Matching Skills</h3>
              <div className="space-y-2">
                {alignment.matching_skills.map((s, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{s.skill_name}</span>
                    <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700">{(s.weight * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Missing skills */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Missing Skills</h3>
              <div className="space-y-2">
                {alignment.missing_skills.map((s, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{s.skill_name}</span>
                    <span className="text-xs px-2 py-1 rounded-full bg-red-100 text-red-700">{(s.weight * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-16 bg-white rounded-xl shadow-sm border border-gray-100">
          <BriefcaseIcon className="h-12 w-12 text-gray-300 mx-auto" />
          <p className="mt-2 text-gray-600">Select a role and analyze to see alignment</p>
        </div>
      )}
    </div>
  )
}
