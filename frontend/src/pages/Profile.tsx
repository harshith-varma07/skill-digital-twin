import { useRef, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { userService } from '../services/api'
import { useAuthStore } from '../store/authStore'
import { UserCircleIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function Profile() {
  const { user, loadUser } = useAuthStore()
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  const { data: completeness } = useQuery({
    queryKey: ['profile-completeness'],
    queryFn: async () => {
      const response = await userService.getProfileCompleteness()
      return response.data as { percentage: number; missing_fields: string[] }
    },
  })

  const uploadResume = useMutation({
    mutationFn: async (file: File) => userService.uploadResume(file),
    onSuccess: () => {
      toast.success('Resume uploaded and processed')
      queryClient.invalidateQueries({ queryKey: ['user-profile'] })
      loadUser()
    },
  })

  const updateProfile = useMutation({
    mutationFn: async (data: Record<string, unknown>) => userService.updateProfile(data),
    onSuccess: () => {
      toast.success('Profile updated')
      loadUser()
    },
  })

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) uploadResume.mutate(file)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
          <p className="text-gray-600">Manage your personal information and resume</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Profile Card */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 rounded-full bg-primary-100 flex items-center justify-center">
              <UserCircleIcon className="h-10 w-10 text-primary-600" />
            </div>
            <div>
              <p className="text-lg font-semibold text-gray-900">{user?.full_name}</p>
              <p className="text-sm text-gray-600">{user?.email}</p>
            </div>
          </div>

          <div className="mt-6">
            <label className="block text-sm text-gray-600 mb-2">Profile Completeness</label>
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${completeness?.percentage || 0}%` }}
              />
            </div>
            <p className="mt-1 text-sm text-gray-600">{completeness?.percentage?.toFixed(0) || 0}% completed</p>
            {completeness?.missing_fields?.length ? (
              <p className="mt-2 text-xs text-gray-500">Missing: {completeness.missing_fields.join(', ')}</p>
            ) : null}
          </div>
        </div>

        {/* Resume Upload */}
        <div className="md:col-span-2 bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Resume</h2>
              <p className="text-sm text-gray-600">Upload your resume to extract skills</p>
            </div>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              <ArrowUpTrayIcon className="h-5 w-5" /> Upload PDF
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.doc,.docx"
              className="hidden"
              onChange={onFileChange}
            />
          </div>

          <div className="mt-6 p-4 rounded-lg bg-gray-50 text-sm text-gray-600">
            Accepted formats: PDF, DOC, DOCX. Max size 10MB.
          </div>
        </div>
      </div>

      {/* Editable fields could go here if supported */}
    </div>
  )
}
