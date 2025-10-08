const $ = (sel) => document.querySelector(sel);
const deviceKey = 'qa_device_id';

function getDeviceId() {
  return $('#deviceId').value.trim();
}

function setSavedDeviceId(id) {
  localStorage.setItem(deviceKey, id);
}

function getSavedDeviceId() {
  return localStorage.getItem(deviceKey) || '';
}

async function refreshDocs() {
  const deviceId = getDeviceId();
  if (!deviceId) { alert('Set Device ID first'); return; }
  const res = await fetch(`/documents?device_id=${encodeURIComponent(deviceId)}`);
  let data;
  try { data = await res.json(); } catch { data = {}; }
  if (!res.ok) {
    alert(`List failed: ${data.error || res.statusText}${data.detail ? ' - ' + data.detail : ''}`);
    return;
  }
  const list = $('#docList');
  const select = $('#docSelect');
  list.innerHTML = '';
  select.innerHTML = '<option value="">All documents</option>';
  for (const doc of (data.documents || [])) {
    const li = document.createElement('li');
    li.innerHTML = `
      <span>${doc.filename} <small style="color:#9ca3af">(${doc._id})</small></span>
      <div>
        <button data-docid="${doc._id}" class="useBtn">Use</button>
        <button data-docid="${doc._id}" class="delBtn">Delete</button>
      </div>
    `;
    list.appendChild(li);

    const opt = document.createElement('option');
    opt.value = doc._id;
    opt.textContent = doc.filename;
    select.appendChild(opt);
  }

  // Bind delete
  list.querySelectorAll('.delBtn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.getAttribute('data-docid');
      const delRes = await fetch(`/documents/${encodeURIComponent(id)}?device_id=${encodeURIComponent(deviceId)}`, { method: 'DELETE' });
      let delData; try { delData = await delRes.json(); } catch { delData = {}; }
      if (!delRes.ok) {
        alert(`Delete failed: ${delData.error || delRes.statusText}${delData.detail ? ' - ' + delData.detail : ''}`);
        return;
      }
      await refreshDocs();
    });
  });

  // Bind use -> sets dropdown
  list.querySelectorAll('.useBtn').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-docid');
      $('#docSelect').value = id;
    });
  });
}

async function uploadFile(e) {
  e.preventDefault();
  const deviceId = getDeviceId();
  if (!deviceId) { alert('Set Device ID first'); return; }
  const file = $('#fileInput').files[0];
  if (!file) { alert('Choose a PDF'); return; }
  const fd = new FormData();
  fd.append('device_id', deviceId);
  fd.append('file', file);
  $('#uploadStatus').textContent = 'Uploading...';
  try {
    const res = await fetch('/documents/upload', { method: 'POST', body: fd });
    let data; try { data = await res.json(); } catch { data = {}; }
    if (!res.ok) throw new Error(`${data.error || 'Upload failed'}${data.detail ? ' - ' + data.detail : ''}`);
    $('#uploadStatus').textContent = `Uploaded: doc_id=${data.doc_id}, chunks=${data.chunks_indexed}`;
    await refreshDocs();
  } catch (err) {
    $('#uploadStatus').textContent = `Error: ${err.message}`;
  }
}

async function askQuestion() {
  const deviceId = getDeviceId();
  if (!deviceId) { alert('Set Device ID first'); return; }
  const question = $('#questionInput').value.trim();
  if (!question) { alert('Enter a question'); return; }
  const docId = $('#docSelect').value || undefined;
  $('#answer').textContent = 'Thinking...';
  $('#sources').textContent = '';
  const res = await fetch('/qa/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ device_id: deviceId, question, doc_id: docId })
  });
  let data; try { data = await res.json(); } catch { data = {}; }
  if (!res.ok) {
    $('#answer').textContent = `Error: ${data.error || res.statusText}${data.detail ? ' - ' + data.detail : ''}`;
    return;
  }
  $('#answer').textContent = data.answer || '';
  const sources = (data.sources || []).map(s => `${s.source || 'doc'} (page ${s.page ?? '?'})`).join('\n');
  $('#sources').textContent = sources ? `Sources:\n${sources}` : '';
}

function boot() {
  const saved = getSavedDeviceId();
  if (saved) { $('#deviceId').value = saved; }
  $('#saveDevice').addEventListener('click', () => {
    const id = getDeviceId();
    if (!id) { alert('Enter a Device ID'); return; }
    setSavedDeviceId(id);
    refreshDocs();
  });
  $('#uploadForm').addEventListener('submit', uploadFile);
  $('#refreshDocs').addEventListener('click', refreshDocs);
  $('#askBtn').addEventListener('click', askQuestion);
}

document.addEventListener('DOMContentLoaded', boot);
