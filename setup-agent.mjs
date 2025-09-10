import axios from 'axios';

const knowledgeBaseId = 'knl_1w6qAIzHkAlCQr2c01lfe';  // Your existing KB ID

const api = axios.create({
  baseURL: 'https://api.d-id.com',
  headers: {
    Authorization: `Basic bWFtbXlsb2xpYW51QGdtYWlsLmNvbQ:2Bb1KDlp9aPmhiXP3_Z-1`, // Replace with your actual API key
    'Content-Type': 'application/json'
  }
});

async function createAgent() {
  const { data: agent } = await api.post('/agents', {
    name: 'Custom Avatar Agent',
    description: 'Explains topics with a customized face and friendly tone.',
    knowledgeId: knowledgeBaseId,
    config: {
      voice: "en-US-Wavenet-H",
      personality: "Friendly, calm, caring and informative guide",
      sourceURL: 'https://drive.google.com/uc?export=download&id=1v2OB75UXlopQ-WeuQSExjE0dguzl3hPo', // Direct image link
    }
  });

  console.log('✅ Agent Created!');
  console.log('🤖 Agent ID:', agent.id);
  return agent.id;
}

createAgent();
