import { useCallback, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import ForceGraph2D, { ForceGraphMethods, NodeObject } from 'react-force-graph-2d'
import { digitalTwinService, skillService } from '../services/api'
import {
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  ArrowsPointingOutIcon,
} from '@heroicons/react/24/outline'

interface SkillNode {
  id: string
  name: string
  mastery_level: number
  category: string
  is_user_skill: boolean
}

interface SkillLink {
  source: string
  target: string
  relationship: string
}

interface VisualizationData {
  nodes: SkillNode[]
  links: SkillLink[]
}

const categoryColors: Record<string, string> = {
  'Programming Languages': '#3b82f6',
  'Frameworks': '#8b5cf6',
  'Databases': '#10b981',
  'Cloud & DevOps': '#f59e0b',
  'Data Science': '#ec4899',
  'Soft Skills': '#06b6d4',
  'Tools': '#6366f1',
  'Other': '#6b7280',
}

export default function DigitalTwin() {
  const graphRef = useRef<ForceGraphMethods>()
  const [selectedNode, setSelectedNode] = useState<SkillNode | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCategory, setFilterCategory] = useState<string>('')
  const [showUserSkillsOnly, setShowUserSkillsOnly] = useState(false)

  const { data: vizData, isLoading } = useQuery({
    queryKey: ['visualization-data'],
    queryFn: async () => {
      const response = await digitalTwinService.getVisualizationData()
      return response.data as VisualizationData
    },
  })

  const { data: categories } = useQuery({
    queryKey: ['skill-categories'],
    queryFn: async () => {
      const response = await skillService.getCategories()
      return response.data as Array<{ id: number; name: string }>
    },
  })

  // Filter nodes based on search and filters
  const filteredData = useCallback(() => {
    if (!vizData) return { nodes: [], links: [] }

    let nodes = [...vizData.nodes]
    
    if (searchTerm) {
      nodes = nodes.filter(n => 
        n.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }
    
    if (filterCategory) {
      nodes = nodes.filter(n => n.category === filterCategory)
    }
    
    if (showUserSkillsOnly) {
      nodes = nodes.filter(n => n.is_user_skill)
    }

    const nodeIds = new Set(nodes.map(n => n.id))
    const links = vizData.links.filter(
      l => nodeIds.has(l.source as string) && nodeIds.has(l.target as string)
    )

    return { nodes, links }
  }, [vizData, searchTerm, filterCategory, showUserSkillsOnly])

  const handleNodeClick = useCallback((node: NodeObject) => {
    setSelectedNode(node as unknown as SkillNode)
    if (graphRef.current) {
      graphRef.current.centerAt(node.x, node.y, 1000)
      graphRef.current.zoom(2, 1000)
    }
  }, [])

  const handleBackgroundClick = useCallback(() => {
    setSelectedNode(null)
  }, [])

  const getMasteryColor = (level: number) => {
    if (level >= 80) return '#10b981'
    if (level >= 60) return '#3b82f6'
    if (level >= 40) return '#f59e0b'
    return '#ef4444'
  }

  const nodeCanvasObject = useCallback((node: NodeObject, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const skillNode = node as unknown as SkillNode & NodeObject
    const label = skillNode.name
    const fontSize = 12 / globalScale
    const nodeSize = skillNode.is_user_skill ? 8 : 5
    
    // Node circle
    ctx.beginPath()
    ctx.arc(node.x!, node.y!, nodeSize, 0, 2 * Math.PI)
    ctx.fillStyle = skillNode.is_user_skill 
      ? getMasteryColor(skillNode.mastery_level)
      : categoryColors[skillNode.category] || '#6b7280'
    ctx.fill()
    
    // Outer ring for user skills
    if (skillNode.is_user_skill) {
      ctx.beginPath()
      ctx.arc(node.x!, node.y!, nodeSize + 2, 0, 2 * Math.PI)
      ctx.strokeStyle = getMasteryColor(skillNode.mastery_level)
      ctx.lineWidth = 2 / globalScale
      ctx.stroke()
    }
    
    // Label
    ctx.font = `${fontSize}px Inter, sans-serif`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'top'
    ctx.fillStyle = '#374151'
    ctx.fillText(label, node.x!, node.y! + nodeSize + 2)
  }, [])

  const resetView = useCallback(() => {
    if (graphRef.current) {
      graphRef.current.zoomToFit(400)
    }
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  const graphData = filteredData()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Skill Digital Twin</h1>
          <p className="text-gray-600">
            Interactive visualization of your skill network
          </p>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div className="flex flex-wrap gap-4 items-center">
          {/* Search */}
          <div className="relative flex-1 min-w-[200px]">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search skills..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Category Filter */}
          <div className="flex items-center gap-2">
            <AdjustmentsHorizontalIcon className="h-5 w-5 text-gray-400" />
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-3 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Categories</option>
              {categories?.map(cat => (
                <option key={cat.id} value={cat.name}>{cat.name}</option>
              ))}
            </select>
          </div>

          {/* User Skills Toggle */}
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showUserSkillsOnly}
              onChange={(e) => setShowUserSkillsOnly(e.target.checked)}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700">My skills only</span>
          </label>

          {/* Reset View */}
          <button
            onClick={resetView}
            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowsPointingOutIcon className="h-5 w-5" />
            Reset View
          </button>
        </div>

        {/* Legend */}
        <div className="mt-4 flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-gray-600">Expert (80%+)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-blue-500" />
            <span className="text-gray-600">Proficient (60-79%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className="text-gray-600">Intermediate (40-59%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-gray-600">Beginner (&lt;40%)</span>
          </div>
        </div>
      </div>

      {/* Graph Container */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden" style={{ height: '600px' }}>
          <ForceGraph2D
            ref={graphRef}
            graphData={graphData}
            nodeId="id"
            nodeLabel="name"
            nodeCanvasObject={nodeCanvasObject}
            nodePointerAreaPaint={(node, color, ctx) => {
              ctx.fillStyle = color
              ctx.beginPath()
              ctx.arc(node.x!, node.y!, 10, 0, 2 * Math.PI)
              ctx.fill()
            }}
            linkColor={() => '#e5e7eb'}
            linkWidth={1}
            onNodeClick={handleNodeClick}
            onBackgroundClick={handleBackgroundClick}
            cooldownTicks={100}
            d3VelocityDecay={0.3}
          />
        </div>

        {/* Skill Details Panel */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            {selectedNode ? 'Skill Details' : 'Select a Skill'}
          </h2>
          
          {selectedNode ? (
            <div className="space-y-4">
              <div>
                <h3 className="text-xl font-bold text-gray-900">{selectedNode.name}</h3>
                <p className="text-sm text-gray-500">{selectedNode.category}</p>
              </div>

              {selectedNode.is_user_skill && (
                <div>
                  <p className="text-sm text-gray-600 mb-1">Mastery Level</p>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-gray-100 rounded-full h-3">
                      <div
                        className="h-3 rounded-full transition-all"
                        style={{
                          width: `${selectedNode.mastery_level}%`,
                          backgroundColor: getMasteryColor(selectedNode.mastery_level),
                        }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-700">
                      {selectedNode.mastery_level}%
                    </span>
                  </div>
                </div>
              )}

              {!selectedNode.is_user_skill && (
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">
                    You haven't added this skill yet. Consider adding it to track your progress!
                  </p>
                  <button className="mt-2 text-sm text-primary-600 hover:text-primary-700 font-medium">
                    + Add to my skills
                  </button>
                </div>
              )}

              {/* Related Skills */}
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Related Skills</p>
                <div className="flex flex-wrap gap-2">
                  {vizData?.links
                    .filter(l => l.source === selectedNode.id || l.target === selectedNode.id)
                    .slice(0, 5)
                    .map((link, i) => {
                      const relatedId = link.source === selectedNode.id ? link.target : link.source
                      const relatedNode = vizData.nodes.find(n => n.id === relatedId)
                      return relatedNode ? (
                        <span
                          key={i}
                          className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full"
                        >
                          {relatedNode.name}
                        </span>
                      ) : null
                    })}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500">
                Click on a node in the graph to see skill details
              </p>
            </div>
          )}

          {/* Stats */}
          <div className="mt-6 pt-6 border-t border-gray-100">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Network Stats</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Total Skills</span>
                <span className="font-medium">{graphData.nodes.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Your Skills</span>
                <span className="font-medium">
                  {graphData.nodes.filter(n => n.is_user_skill).length}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Connections</span>
                <span className="font-medium">{graphData.links.length}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
