const ML_API_URL = import.meta.env.VITE_ML_API_URL ?? "http://egoai.duckdns.org:8001";

export async function chatWithML(message: string, history?: any, calendar?: any) {
  try {
    const response = await fetch(`${ML_API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history, calendar }),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`ML chat failed: ${response.status} - ${errorText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error in chatWithML:", error);
    throw new Error(`ML service unavailable: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

export async function voiceChatWithML(file: File) {
  try {
    const formData = new FormData();
    formData.append("file", file);
    
    const response = await fetch(`${ML_API_URL}/voice`, {
      method: "POST",
      body: formData,
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`ML voice chat failed: ${response.status} - ${errorText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error in voiceChatWithML:", error);
    throw new Error(`ML voice service unavailable: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}
