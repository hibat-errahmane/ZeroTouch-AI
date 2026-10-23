async function getJSON(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'The request could not be completed.');
  return data;
}
async function refreshHealth() {
  if (!document.querySelector('#app-status')) return;
  try {
    const health = await getJSON('/api/health');
    document.querySelector('#app-status').textContent = 'Healthy';
    document.querySelector('#document-count').textContent = health.counts.documents;
  } catch (_) { document.querySelector('#app-status').textContent = 'Unavailable'; }
}
async function refreshAI() {
  if (!document.querySelector('#ai-status')) return;
  try {
    const ai = await getJSON('/api/ollama');
    document.querySelector('#ai-status').textContent = ai.available ? (ai.model_installed ? 'Connected' : 'Model missing') : 'Offline';
    document.querySelector('#ai-detail').textContent = ai.available ? ai.model : 'Optional in Phase 1 · preview works offline';
  } catch (_) { document.querySelector('#ai-status').textContent = 'Unavailable'; }
}
const form = document.querySelector('#upload-form');
if (form) form.addEventListener('submit', async event => {
  event.preventDefault();
  const button = document.querySelector('#upload-button');
  const status = document.querySelector('#upload-status');
  document.querySelector('#preview-panel').hidden = true;
  button.disabled = true;
  status.className = '';
  status.textContent = 'Reading your document…';
  try {
    const data = await getJSON('/api/documents', {method:'POST', body:new FormData(form)});
    document.querySelector('#preview-name').textContent = data.name;
    document.querySelector('#preview').textContent = data.text;
    document.querySelector('#preview-panel').hidden = false;
    status.textContent = 'Document saved locally. Text preview is ready.';
    await refreshHealth();
  } catch (error) { status.className = 'error'; status.textContent = error.message; }
  finally { button.disabled = false; }
});
refreshHealth();
refreshAI();
