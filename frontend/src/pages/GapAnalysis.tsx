import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { digitalTwinService, careerService } from '../services/api'
import { AdjustmentsHorizontalIcon, FunnelIcon, BriefcaseIcon } from '@heroicons/react/24/outline'

interface GapSkill {
  skill_id: number
  skill_name: string
  current_mastery: number
  target_mastery: number
  gap: number
  priority: 'high' | 'medium' | 'low'
}

interface GapAnalysisResult {
  gap_score: number
  total_skills: number
  skills: GapSkill[]
}

export default function GapAnalysis() {
  const [selectedRole, setSelectedRole] = useState<number | ''>('')
  const [priorityFilter, setPriorityFilter] = useState<string>('')
  const [minGap, setMinGap] = useState<number>(0)

  const { data: roles } = useQuery({
    queryKey: ['career-roles'],
    queryFn: async () => {
      const response = await careerService.getRoles()
      return response.data as Array<{ id: number; title: string; level: string }>
    },
  })

  const { data: gapAnalysis, isLoading, refetch } = useQuery({
    queryKey: ['gap-analysis', selectedRole],
    enabled: false,
    queryFn: async () => {
      const response = await digitalTwinService.getGapAnalysis(
        typeof selectedRole === 'number' ? selectedRole : undefined
      )
      return response.data as GapAnalysisResult
    },
  })

  const filteredSkills = (gapAnalysis?.skills || []).filter(s => {
    if (priorityFilter && s.priority !== priorityFilter) return false
    if (minGap && s.gap < minGap) return false
    return true
  })

  const handleAnalyze = () => {
    refetch()
  }

  const getPriorityBadge = (priority: GapSkill['priority']) => {
    const map = {
      high: 'bg-red-100 text-red-700',
      medium: 'bg-yellow-100 text-yellow-700',
      low: 'bg-green-100 text-green-700',
    }
    return map[priority]
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gap Analysis</h1>
          <p className="text-gray-600">Compare your skills to role requirements</p>
        </div>
      </div>

      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Target Role</label>
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

          <div>
            <label className="block text-sm text-gray-600 mb-1">Priority</label>
            <div className="relative">
              <FunnelIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <select
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">All</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-1">Minimum Gap</label>
            <div className="flex items-center gap-3">
              <input
                type="range"
                min={0}
                max={100}
                value={minGap}
                onChange={(e) => setMinGap(parseInt(e.target.value))}
                className="w-full"
              />
              <span className="text-sm text-gray-600">{minGap}%</span>
            </div>
          </div>

          <div className="flex items-end">
            <button
              onClick={handleAnalyze}
              className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Analyze Gaps
            </button>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full" />
        </div>
      ) : gapAnalysis ? (
        <div className="space-y-6">
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Overall Gap Score</p>
                <p className="text-3xl font-bold text-gray-900">{gapAnalysis.gap_score.toFixed(0)}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Skills Considered</p>
                <p className="text-3xl font-bold text-gray-900">{gapAnalysis.total_skills}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Skill</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Target</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gap</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Priority</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredSkills.map(skill => (
                  <tr key={skill.skill_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{skill.skill_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="w-40 bg-gray-100 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${skill.current_mastery}%` }} />
                      </div>
                      <span className="text-xs text-gray-500">{skill.current_mastery}%</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="w-40 bg-gray-100 rounded-full h-2">
                        <div className="bg-green-600 h-2 rounded-full" style={{ width: `${skill.target_mastery}%` }} />
                      </div>
                      <span className="text-xs text-gray-500">{skill.target_mastery}%</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{skill.gap}%</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full font-medium ${getPriorityBadge(skill.priority)}`}>
                        {skill.priority}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="text-center py-16 bg-white rounded-xl shadow-sm border border-gray-100">
          <AdjustmentsHorizontalIcon className="h-12 w-12 text-gray-300 mx-auto" />
          <p className="mt-2 text-gray-600">Select a target role and analyze to see results</p>
        </div>
      )}
    </div>
  )
}
