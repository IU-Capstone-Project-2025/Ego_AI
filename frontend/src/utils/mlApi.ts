const ML_API_URL = import.meta.env.VITE_ML_API_URL ?? "http://185.207.133.14:8001";

export async function chatWithML(message: string, history?: any, calendar?: any) {
  const response = await fetch(`${ML_API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history, calendar }),
  });
  if (!response.ok) throw new Error("ML chat failed");
  return response.json();
}

export async function voiceChatWithML(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${ML_API_URL}/voice`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) throw new Error("ML voice chat failed");
  return response.json();
}
