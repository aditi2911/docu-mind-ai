'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const API = process.env.NEXT_PUBLIC_API_URL;

  async function handleSubmit() {
    setLoading(true);
    setStatus('');
    const endpoint = isLogin ? '/auth/login' : '/auth/register';
    try {
      const res = await fetch(`${API}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Something went wrong');
      if (isLogin) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('email', email);
        router.push('/dashboard');
      } else {
        setStatus('✅ Registered! Now login.');
        setIsLogin(true);
      }
    } catch (err: any) {
      setStatus('❌ ' + err.message);
    }
    setLoading(false);
  }

  return (
    <main className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
      <div className="bg-gray-900 rounded-2xl p-8 w-full max-w-md shadow-xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">📄 DocuMind AI</h1>
          <p className="text-gray-400">Ask anything about your documents</p>
        </div>

        <div className="flex rounded-lg bg-gray-800 p-1 mb-6">
          <button
            onClick={() => setIsLogin(true)}
            className={`flex-1 py-2 rounded-md text-sm font-medium transition-all ${isLogin ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
          >
            Login
          </button>
          <button
            onClick={() => setIsLogin(false)}
            className={`flex-1 py-2 rounded-md text-sm font-medium transition-all ${!isLogin ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
          >
            Register
          </button>
        </div>

        <div className="space-y-4">
          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:outline-none focus:border-blue-500"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSubmit()}
            className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-medium py-3 rounded-lg transition-all"
          >
            {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Create Account')}
          </button>
        </div>

        {status && (
          <p className="mt-4 text-center text-sm text-gray-300">{status}</p>
        )}
      </div>
    </main>
  );
}