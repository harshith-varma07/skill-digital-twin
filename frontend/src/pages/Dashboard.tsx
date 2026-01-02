import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { digitalTwinService, careerService, learningService } from '../services/api'
import { useAuthStore } from '../store/authStore'
import {
  CpuChipIcon,
  ChartBarIcon,
  AcademicCapIcon,
  BriefcaseIcon,
  ArrowTrendingUpIcon,
  SparklesIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'

interface SkillSummary {
  total_skills: number
  average_mastery: number
  skills_by_category: Record<string, number>
  strongest_skills: Array<{ name: string; mastery_level: number }>
  weakest_skills: Array<{ name: string; mastery_level: number }>
}

interface CareerRecommendation {
  role: {
    id: number
    title: string
    level: string
  }
  readiness_percentage: number
}

interface LearningRoadmap {
  id: number
  title: string
  progress_percentage: number
}

export default function Dashboard() {
  const { user } = useAuthStore()

  const { data: twinSummary } = useQuery({
    queryKey: ['digital-twin-summary'],
    queryFn: async () => {
      const response = await digitalTwinService.getSummary()
      return response.data as SkillSummary
    },
  })

  const { data: careerRecs } = useQuery({
    queryKey: ['career-recommendations'],
    queryFn: async () => {
      const response = await careerService.getRecommendations()
      return response.data as CareerRecommendation[]
    },
  })

  const { data: roadmaps } = useQuery({
    queryKey: ['learning-roadmaps'],
    queryFn: async () => {
      const response = await learningService.getRoadmaps(true)
      return response.data as LearningRoadmap[]
    },
  })



  const getMasteryColor = (level: number) => {
    if (level >= 80) return 'text-green-600 bg-green-100'
    if (level >= 60) return 'text-blue-600 bg-blue-100'
    if (level >= 40) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.full_name?.split(' ')[0]}!
          </h1>
          <p className="text-gray-600">
            Here's an overview of your Skill Digital Twin
          </p>
        </div>
        <Link
          to="/digital-twin"
          className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <CpuChipIcon className="h-5 w-5 mr-2" />
          View Digital Twin
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Skills</p>
              <p className="text-3xl font-bold text-gray-900">
                {twinSummary?.total_skills || 0}
              </p>
            </div>
            <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <SparklesIcon className="h-6 w-6 text-primary-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Average Mastery</p>
              <p className="text-3xl font-bold text-gray-900">
                {twinSummary?.average_mastery?.toFixed(0) || 0}%
              </p>
            </div>
            <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
              <ArrowTrendingUpIcon className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Active Roadmaps</p>
              <p className="text-3xl font-bold text-gray-900">
                {roadmaps?.length || 0}
              </p>
            </div>
            <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <AcademicCapIcon className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Career Matches</p>
              <p className="text-3xl font-bold text-gray-900">
                {careerRecs?.filter(r => r.readiness_percentage >= 50).length || 0}
              </p>
            </div>
            <div className="h-12 w-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <BriefcaseIcon className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Strongest Skills */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Top Skills</h2>
            <Link to="/digital-twin" className="text-sm text-primary-600 hover:text-primary-700">
              View all
            </Link>
          </div>
          <div className="space-y-3">
            {twinSummary?.strongest_skills?.slice(0, 5).map((skill, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{skill.name}</span>
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${getMasteryColor(skill.mastery_level)}`}>
                  {skill.mastery_level}%
                </span>
              </div>
            )) || (
              <p className="text-sm text-gray-500">No skills recorded yet</p>
            )}
          </div>
        </div>

        {/* Skills to Improve */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Skills to Improve</h2>
            <Link to="/gap-analysis" className="text-sm text-primary-600 hover:text-primary-700">
              Gap Analysis
            </Link>
          </div>
          <div className="space-y-3">
            {twinSummary?.weakest_skills?.slice(0, 5).map((skill, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{skill.name}</span>
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${getMasteryColor(skill.mastery_level)}`}>
                  {skill.mastery_level}%
                </span>
              </div>
            )) || (
              <p className="text-sm text-gray-500">No skills to show</p>
            )}
          </div>
        </div>

        {/* Career Readiness */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Career Matches</h2>
            <Link to="/careers" className="text-sm text-primary-600 hover:text-primary-700">
              Explore
            </Link>
          </div>
          <div className="space-y-3">
            {careerRecs?.slice(0, 5).map((rec, index) => (
              <div key={index} className="flex items-center justify-between">
                <div>
                  <span className="text-sm text-gray-700">{rec.role.title}</span>
                  <span className="text-xs text-gray-400 ml-2">{rec.role.level}</span>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${getMasteryColor(rec.readiness_percentage)}`}>
                  {rec.readiness_percentage.toFixed(0)}%
                </span>
              </div>
            )) || (
              <p className="text-sm text-gray-500">Add skills to see matches</p>
            )}
          </div>
        </div>
      </div>

      {/* Learning Progress */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Active Learning Paths</h2>
          <Link to="/learning" className="text-sm text-primary-600 hover:text-primary-700">
            View all
          </Link>
        </div>
        {roadmaps && roadmaps.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {roadmaps.slice(0, 3).map((roadmap) => (
              <Link
                key={roadmap.id}
                to={`/learning?roadmap=${roadmap.id}`}
                className="p-4 border border-gray-100 rounded-lg hover:border-primary-200 hover:bg-primary-50 transition-all"
              >
                <h3 className="font-medium text-gray-900">{roadmap.title}</h3>
                <div className="mt-3">
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-500">Progress</span>
                    <span className="font-medium text-gray-700">{roadmap.progress_percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${roadmap.progress_percentage}%` }}
                    />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <AcademicCapIcon className="h-12 w-12 text-gray-300 mx-auto" />
            <p className="mt-2 text-gray-500">No active learning paths</p>
            <Link
              to="/learning"
              className="mt-3 inline-flex items-center text-sm text-primary-600 hover:text-primary-700"
            >
              Create a learning path
            </Link>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link
          to="/assessments"
          className="flex items-center p-4 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl text-white hover:from-primary-600 hover:to-primary-700 transition-all card-hover"
        >
          <ChartBarIcon className="h-8 w-8 mr-3" />
          <div>
            <h3 className="font-semibold">Take Assessment</h3>
            <p className="text-sm text-primary-100">Evaluate your skill level</p>
          </div>
        </Link>

        <Link
          to="/gap-analysis"
          className="flex items-center p-4 bg-gradient-to-r from-secondary-500 to-secondary-600 rounded-xl text-white hover:from-secondary-600 hover:to-secondary-700 transition-all card-hover"
        >
          <ArrowTrendingUpIcon className="h-8 w-8 mr-3" />
          <div>
            <h3 className="font-semibold">Gap Analysis</h3>
            <p className="text-sm text-secondary-100">Find skills to develop</p>
          </div>
        </Link>

        <Link
          to="/profile"
          className="flex items-center p-4 bg-gradient-to-r from-green-500 to-green-600 rounded-xl text-white hover:from-green-600 hover:to-green-700 transition-all card-hover"
        >
          <ClockIcon className="h-8 w-8 mr-3" />
          <div>
            <h3 className="font-semibold">Update Profile</h3>
            <p className="text-sm text-green-100">Upload resume & more</p>
          </div>
        </Link>
      </div>
    </div>
  )
}
