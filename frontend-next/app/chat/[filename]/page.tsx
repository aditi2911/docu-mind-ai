'use client';
import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

interface Message {
  role: 'user' | 'bot';
  content: string;
  isGrounded?: boolean;
  attempts?: number;
}

export default function Chat({ params }: { params: any }) {
  const [filename, setFilename] = useState('');

  useEffect(() => {
    const resolveParams = async () => {
      const resolved = await Promise.resolve(params);
      const raw = resolved?.filename || '';
      setFilename(decodeURIComponent(raw));
    };
    resolveParams();
  }, [params]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const API = process.env.NEXT_PUBLIC_API_URL;

useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/'); return; }
    setMessages([{
      role: 'bot',
      content: `Hi! I've loaded "${filename}". Ask me anything about it.`,
    }]);
  }, [filename]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function sendMessage() {
    if (!question.trim() || loading) return;
    const token = localStorage.getItem('token');
    if (!token) { router.push('/'); return; }
    const userMsg: Message = { role: 'user', content: question };
    setMessages(prev => [...prev, userMsg]);
    setQuestion('');
    setLoading(true);
    setMessages(prev => [...prev, { role: 'bot', content: '...' }]);
    try {
      const res = await fetch(`${API}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ filename, question })
      });
      const data = await res.json();
      setMessages(prev => [
        ...prev.slice(0, -1),
        {
          role: 'bot',
          content: data.answer || data.detail || 'Something went wrong.',
          isGrounded: data.is_grounded,
          attempts: data.attempts
        }
      ]);
    } catch (err: any) {
      setMessages(prev => [
        ...prev.slice(0, -1),
        { role: 'bot', content: '❌ Error: ' + err.message }
      ]);
    }
    setLoading(false);
  }

  return (
    <main className="min-h-screen bg-gray-950 text-white flex flex-col">
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <button onClick={() => router.push('/dashboard')} className="text-gray-400 hover:text-white transition-all">
            ← Back
          </button>
          <div>
            <h1 className="text-sm font-semibold">📄 {filename}</h1>
            <p className="text-xs text-gray-500">DocuMind AI</p>
          </div>
        </div>
      </header>
      <div className="flex-1 overflow-y-auto p-6 space-y-4 max-w-3xl mx-auto w-full">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-100'}`}>
              <p className="text-sm whitespace-pre-wrap">
                {msg.content === '...' ? <span className="animate-pulse">Thinking...</span> : msg.content}
              </p>
              {msg.role === 'bot' && msg.isGrounded !== undefined && (
                <div className={`mt-2 text-xs ${msg.isGrounded ? 'text-green-400' : 'text-yellow-400'}`}>
                  {msg.isGrounded ? '✓ Grounded' : '⚠ Unverified'} · {msg.attempts} attempt(s)
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <div className="bg-gray-900 border-t border-gray-800 p-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input
            type="text"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendMessage()}
            placeholder="Ask a question about the document..."
            disabled={loading}
            className="flex-1 bg-gray-800 text-white rounded-xl px-4 py-3 border border-gray-700 focus:outline-none focus:border-blue-500 disabled:opacity-50"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !question.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white px-6 py-3 rounded-xl font-medium transition-all"
          >
            {loading ? '...' : 'Ask'}
          </button>
        </div>
      </div>
    </main>
  );
}