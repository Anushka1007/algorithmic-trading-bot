import { useEffect, useState } from 'react'

function App() {
  const [status, setStatus] = useState<string>("Loading...")

  useEffect(() => {
    fetch('http://localhost:8000/api/health')
      .then(res => res.json())
      .then(data => setStatus(data.message || data.status))
      .catch(() => setStatus("Backend offline"))
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full text-center">
        <h1 className="text-3xl font-bold mb-4 text-blue-600">Algorithmic Trading Bot</h1>
        <p className="text-gray-600 mb-6">Educational paper-trading platform</p>
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-100">
          <p className="text-sm text-gray-500 font-semibold uppercase tracking-wider mb-1">Backend Status</p>
          <p className={`text-lg font-medium ${status === 'Backend is running' ? 'text-green-600' : 'text-amber-500'}`}>
            {status}
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
