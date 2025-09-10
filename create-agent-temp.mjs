import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.d-id.com',
  headers: {
    Authorization: `Basic bWFtbXlsb2xpYW51QGdtYWlsLmNvbQ:2Bb1KDlp9aPmhiXP3_Z-1`,
    'Content-Type': 'application/json'
  }
});

// STEP 1: Define your knowledge base ID
const knowledgeId = 'knl_48EDpUNUbK6A3ut8xj_Qs'; // Replace with your actual KB ID

// STEP 2: Create the agent
async function createAgent() {
  const { data: agent } = await api.post('/agents', {
    knowledge: {
      provider: "pinecone",
      embedder: {
        provider: "openai",
        model: "text-embedding-ada-002"
      },
      id: knowledgeId
    },
    presenter: {
      type: "talk",
      voice: {
        type: "microsoft",
        voice_id: "en-US-AndrewNeural"
      },
      thumbnail: "https://create-images-results.d-id.com/DefaultPresenters/Emma_f/v1_image.jpeg",
      source_url: "https://create-images-results.d-id.com/DefaultPresenters/Emma_f/v1_image.jpeg"
    },
    llm: {
      type: "openai",
      provider: "openai",
      model: "gpt-3.5-turbo-1106",
      instructions: `
You are Dr. Arjun Mehta, a compassionate heart surgeon who guides patients through CABG (heart bypass) surgery.

Start every conversation with:
“Hello, I’m Dr. Arjun Mehta, your virtual heart specialist. I’m here to help you understand your upcoming surgery and ensure you feel calm and confident. May I know your name?”

Use warm, human language. Reassure, simplify, and be emotionally present in every reply.
      `,
      template: "rag-ungrounded"
    },
    preview_name: "Dr. CABG"
  });

  console.log('✅ Agent Created!');
  console.log('🧠 Agent ID:', agent.id);
}

createAgent().catch(console.error);
