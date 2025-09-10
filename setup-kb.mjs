import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.d-id.com',
  headers: {
    Authorization: `Basic bWFtbXlsb2xpYW51QGdtYWlsLmNvbQ:2Bb1KDlp9aPmhiXP3_Z-1`, // your actual key
    'Content-Type': 'application/json'
  }
});

async function setupKnowledgeBase() {
  // STEP 1: Create KB
  const { data: kb } = await api.post('/knowledge', {
    name: 'CABG Patient Education',
    description: 'Guide to coronary artery bypass graft (CABG) surgery'
  });
  console.log('✅ Knowledge Base Created:', kb.id);

  // STEP 2: Upload the PDF to it
  const { data: upload } = await api.post(`/knowledge/${kb.id}/documents`, {
    documentType: 'pdf',
    source_url: 'https://drive.google.com/uc?export=download&id=1eqTxYZNcu4fMTo3ba1g0EgJrXZxvwiF6',
    title: 'CABG Surgery Guide'
  });

  console.log('📄 Document Uploaded:', upload.id);
  return kb.id;
}

setupKnowledgeBase().catch(console.error);
