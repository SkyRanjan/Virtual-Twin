import axios from 'axios';

const knowledgeBaseId = 'knl_QC-WWA1j_KwXZpuiHPjrJ';  // from step 1

const api = axios.create({
  baseURL: 'https://api.d-id.com',
  headers: {
    Authorization: `Basic bWFtbXlsb2xpYW51QGdtYWlsLmNvbQ:2Bb1KDlp9aPmhiXP3_Z-1`,
    'Content-Type': 'application/json'
  }
});

async function createAgent() {
  const { data: agent } = await api.post('/agents', {
    name: 'Dr. CABG Assistant',
    description: 'Explains heart bypass surgery to patients in a friendly tone.',
    knowledgeId: knowledgeBaseId,
    config: {
      voice: "en-US-Wavenet-D",
      personality: "Friendly, calm, and informative doctor",
      sourceURL: 'https://drive.google.com/file/d/1eqTxYZNcu4fMTo3ba1g0EgJrXZxvwiF6/view?usp=sharing',
    }
  });

  console.log('✅ Agent Created!');
  console.log('🤖 Agent ID:', agent.id);
  return agent.id;
}

createAgent().catch(console.error);
