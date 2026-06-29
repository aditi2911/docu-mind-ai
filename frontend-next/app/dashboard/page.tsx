'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Dashboard() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [email, setEmail] = useState('');
  const router = useRouter();
  const API = process.env.NEXT_PUBLIC_API_URL;

  async function fetchDocuments(token: string) {
    try {
      const res = await fetch(`${API}/documents`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      console.log('Documents response:', data);
      if (res.ok) setDocuments(data);
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    }
  }

  useEffect(() => {
    const token = localStorage.getItem('token');
    const savedEmail = localStorage.getItem('email');
    console.log('Token found:', !!token);
    if (!token) { router.push('/'); return; }
    if (savedEmail) setEmail(savedEmail);
    fetchDocuments(token);
  }, []);

  async function uploadFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const token = localStorage.getItem('token');
    if (!token) { router.push('/'); return; }
    setUploading(true);
    setUploadStatus('Uploading and processing... (may take 30-60 seconds)');
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch(`${API}/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setUploadStatus(`✅ "${data.filename}" ready — ${data.chunks_created} chunks indexed.`);
        fetchDocuments(token);
      } else {
        setUploadStatus('❌ ' + JSON.stringify(data.detail));
      }
    } catch (err: any) {
      setUploadStatus('❌ Error: ' + err.message);
    }
    setUploading(false);
  }

  function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('email');
    router.push('/');
  }

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">📄 DocuMind AI</h1>
        <div className="flex items-center gap-4">
          <span className="text-gray-400 text-sm">{email}</span>
          <button onClick={logout} className="text-sm bg-gray-800 hover:bg-gray-700 px-3 py-1 rounded-lg">
            Logout
          </button>
        </div>
      </header>

      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-gray-900 rounded-2xl p-6 mb-6 border border-gray-800">
          <h2 className="text-lg font-semibold mb-4">Upload a Document</h2>
          <label className={`flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-xl cursor-pointer transition-all ${uploading ? 'border-gray-600 bg-gray-800' : 'border-gray-600 hover:border-blue-500 hover:bg-gray-800'}`}>
            <div className="text-center">
              <p className="text-gray-400 text-sm">{uploading ? '⏳ Processing...' : '📁 Click to upload a PDF'}</p>
              <p className="text-gray-600 text-xs mt-1">PDF files only</p>
            </div>
            <input type="file" accept=".pdf" className="hidden" onChange={uploadFile} disabled={uploading} />
          </label>
          {uploadStatus && <p className="mt-3 text-sm text-gray-300">{uploadStatus}</p>}
        </div>

        <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
          <h2 className="text-lg font-semibold mb-4 flex justify-between items-center">
            Your Documents
            <button
              onClick={() => fetchDocuments(localStorage.getItem('token') || '')}
              className="text-sm text-blue-400 hover:text-blue-300"
            >
              ↻ Refresh
            </button>
          </h2>
          {documents.length === 0 ? (
            <p className="text-gray-500 text-sm">No documents uploaded yet. Upload a PDF to get started.</p>
          ) : (
            <div className="space-y-3">
              {documents.map((doc, i) => (
                <div key={i} className="flex items-center justify-between bg-gray-800 rounded-xl px-4 py-3">
                  <div>
                    <p className="font-medium text-sm">{doc.filename}</p>
                    <p className="text-gray-500 text-xs mt-0.5">{doc.chunk_count} chunks · {doc.status}</p>
                  </div>
                  <button
                    onClick={() => router.push(`/chat/${encodeURIComponent(doc.filename)}`)}
                    className="bg-blue-600 hover:bg-blue-700 text-white text-sm px-4 py-1.5 rounded-lg"
                  >
                    Chat →
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}