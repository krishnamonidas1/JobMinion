import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../lib/api'
import { X, Plus, Loader, Check } from 'lucide-react'

const JOB_TYPES   = ['Full-time', 'Internship', 'Remote', 'Hybrid', 'Part-time', 'Contract']
const EXP_LEVELS  = ['Fresher (0-1 years)', 'Junior (1-3 years)', 'Mid (3-5 years)', 'Senior (5+ years)']
const POPULAR_ROLES = [
  'Software Engineer', 'Python Developer', 'Full Stack Developer',
  'Frontend Developer', 'Backend Developer', 'Data Scientist',
  'Machine Learning Engineer', 'DevOps Engineer', 'Android Developer',
  'iOS Developer', 'Data Analyst', 'MCA Fresher'
]
const POPULAR_SKILLS = [
  'Python', 'JavaScript', 'React', 'Node.js', 'FastAPI', 'Django',
  'Machine Learning', 'Deep Learning', 'SQL', 'MongoDB', 'AWS',
  'Docker', 'Git', 'TypeScript', 'Java', 'Flutter'
]

function TagInput({ label, placeholder, tags, setTags, suggestions }) {
  const [input,    setInput]    = useState('')
  const [showSugg, setShowSugg] = useState(false)

  const filtered = suggestions?.filter(s =>
    s.toLowerCase().includes(input.toLowerCase()) && !tags.includes(s)
  ) || []

  const addTag = (tag) => {
    const t = tag.trim()
    if (t && !tags.includes(t)) setTags([...tags, t])
    setInput('')
    setShowSugg(false)
  }

  const removeTag = (tag) => setTags(tags.filter(t => t !== tag))

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
      <div className="flex flex-wrap gap-2 mb-2">
        {tags.map(tag => (
          <span key={tag}
            className="flex items-center gap-1 bg-indigo-100 text-indigo-700
                       text-xs px-2.5 py-1 rounded-full font-medium">
            {tag}
            <button onClick={() => removeTag(tag)}
              className="hover:text-indigo-900 transition">
              <X size={12}/>
            </button>
          </span>
        ))}
      </div>
      <div className="relative">
        <input value={input}
          onChange={e => { setInput(e.target.value); setShowSugg(true) }}
          onFocus={() => setShowSugg(true)}
          onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addTag(input) } }}
          placeholder={placeholder}
          className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm
                     focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
        {showSugg && filtered.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-white border
                          border-gray-200 rounded-lg shadow-lg z-10 max-h-40 overflow-y-auto">
            {filtered.slice(0, 8).map(s => (
              <button key={s} type="button"
                onClick={() => addTag(s)}
                className="w-full text-left px-3 py-2 text-sm text-gray-700
                           hover:bg-indigo-50 hover:text-indigo-700 transition">
                {s}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default function Preferences() {
  const navigate = useNavigate()

  const [jobTitles,  setJobTitles]  = useState([])
  const [locations,  setLocations]  = useState([])
  const [jobTypes,   setJobTypes]   = useState([])
  const [experience, setExperience] = useState('')
  const [salaryMin,  setSalaryMin]  = useState('')
  const [salaryMax,  setSalaryMax]  = useState('')
  const [skills,     setSkills]     = useState([])
  const [loading,    setLoading]    = useState(false)
  const [saving,     setSaving]     = useState(false)
  const [saved,      setSaved]      = useState(false)

  useEffect(() => {
    setLoading(true)
    api.get('/preferences/').then(res => {
      const d = res.data
      setJobTitles(d.job_titles  || [])
      setLocations(d.locations   || [])
      setJobTypes(d.job_types    || [])
      setExperience(d.experience || '')
      setSalaryMin(d.salary_min  || '')
      setSalaryMax(d.salary_max  || '')
      setSkills(d.skills         || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      await api.put('/preferences/', {
        job_titles: jobTitles,
        locations,
        job_types:  jobTypes,
        experience: experience || null,
        salary_min: salaryMin  ? parseInt(salaryMin)  : null,
        salary_max: salaryMax  ? parseInt(salaryMax)  : null,
        skills,
      })
      setSaved(true)
      setTimeout(() => navigate('/dashboard'), 1500)
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to save preferences')
    }
    setSaving(false)
  }

  if (loading) return (
    <div className="flex justify-center py-20">
      <Loader size={24} className="animate-spin text-indigo-500"/>
    </div>
  )

  return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Job Preferences</h1>
        <p className="text-gray-500 text-sm mt-1">
          Tell us what you're looking for — we'll scrape and filter jobs accordingly.
        </p>
      </div>

      <div className="space-y-6">

        {/* Job Titles */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <TagInput
            label="Job Titles / Roles"
            placeholder="Type a role and press Enter..."
            tags={jobTitles}
            setTags={setJobTitles}
            suggestions={POPULAR_ROLES}
          />
        </div>

        {/* Location */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <TagInput
            label="Preferred Locations"
            placeholder="Type a city or region and press Enter..."
            tags={locations}
            setTags={setLocations}
            suggestions={['India', 'Bangalore', 'Mumbai', 'Delhi', 'Hyderabad',
                          'Chennai', 'Pune', 'Remote', 'Kolkata', 'Guwahati']}
          />
        </div>

        {/* Job Type */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Job Type
          </label>
          <div className="flex flex-wrap gap-2">
            {JOB_TYPES.map(type => (
              <button key={type} type="button"
                onClick={() => setJobTypes(prev =>
                  prev.includes(type)
                    ? prev.filter(t => t !== type)
                    : [...prev, type]
                )}
                className={`px-4 py-2 rounded-full text-sm font-medium border transition ${
                  jobTypes.includes(type)
                    ? 'bg-indigo-600 text-white border-indigo-600'
                    : 'bg-white text-gray-600 border-gray-300 hover:border-indigo-400'
                }`}>
                {type}
              </button>
            ))}
          </div>
        </div>

        {/* Experience Level */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Experience Level
          </label>
          <div className="space-y-2">
            {EXP_LEVELS.map(level => (
              <label key={level}
                className="flex items-center gap-3 cursor-pointer group">
                <input type="radio" name="experience"
                  checked={experience === level}
                  onChange={() => setExperience(level)}
                  className="w-4 h-4 text-indigo-600 border-gray-300 focus:ring-indigo-500"/>
                <span className={`text-sm ${
                  experience === level ? 'text-indigo-700 font-medium' : 'text-gray-600'
                }`}>{level}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Salary Range */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Expected Salary Range (LPA)
          </label>
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <label className="text-xs text-gray-500 mb-1 block">Minimum</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">
                  ₹
                </span>
                <input type="number" value={salaryMin}
                  onChange={e => setSalaryMin(e.target.value)}
                  placeholder="3"
                  className="w-full border border-gray-300 rounded-lg pl-7 pr-3 py-2.5
                             text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
              </div>
            </div>
            <span className="text-gray-400 mt-5">—</span>
            <div className="flex-1">
              <label className="text-xs text-gray-500 mb-1 block">Maximum</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">
                  ₹
                </span>
                <input type="number" value={salaryMax}
                  onChange={e => setSalaryMax(e.target.value)}
                  placeholder="15"
                  className="w-full border border-gray-300 rounded-lg pl-7 pr-3 py-2.5
                             text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
              </div>
            </div>
          </div>
        </div>

        {/* Skills */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <TagInput
            label="Skills / Tech Stack"
            placeholder="Type a skill and press Enter..."
            tags={skills}
            setTags={setSkills}
            suggestions={POPULAR_SKILLS}
          />
        </div>

        {/* Save Button */}
        <button onClick={handleSave} disabled={saving || saved}
          className="w-full bg-indigo-600 text-white rounded-xl py-3 text-sm font-medium
                     hover:bg-indigo-700 transition disabled:opacity-50
                     flex items-center justify-center gap-2">
          {saved
            ? <><Check size={16}/> Saved! Redirecting...</>
            : saving
            ? <><Loader size={15} className="animate-spin"/> Saving...</>
            : 'Save Preferences'
          }
        </button>
      </div>
    </div>
  )
}