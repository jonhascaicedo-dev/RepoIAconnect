const form = document.getElementById('case-form');
const result = document.getElementById('result');
const summary = document.getElementById('summary');
const status = document.getElementById('status');
const evidence = document.getElementById('evidence');

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>\"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#039;'}[ch]));
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  result.hidden = false;
  status.textContent = 'Procesando...';
  summary.textContent = '';
  evidence.textContent = '';

  const symptom = {
    name: document.getElementById('symptom-name').value.trim(),
    severity: document.getElementById('symptom-severity').value || null,
    duration: document.getElementById('symptom-duration').value.trim() || null
  };

  const examName = document.getElementById('exam-name').value.trim();
  const examination = examName ? {
    name: examName,
    value: document.getElementById('exam-value').value.trim() || null,
    unit: document.getElementById('exam-unit').value.trim() || null
  } : null;

  try {
    const response = await fetch('/api/cases', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        patient_id: document.getElementById('patient-id').value.trim(),
        symptoms: [symptom],
        examinations: examination ? [examination] : []
      })
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.detail || 'Error en la API');

    const detailResponse = await fetch(`/api/cases/${body.case_id}`);
    const detail = await detailResponse.json();
    if (!detailResponse.ok) throw new Error('No se pudo recuperar el caso');

    status.textContent = `Estado: ${detail.status}`;
    summary.innerHTML = `
      <p><strong>Caso:</strong> ${escapeHtml(detail.id)}</p>
      <p><strong>Síntoma:</strong> ${escapeHtml(detail.symptoms[0]?.name)}</p>
      <p><strong>Intensidad:</strong> ${escapeHtml(detail.symptoms[0]?.severity || 'No indicada')}</p>
      <p><strong>Duración:</strong> ${escapeHtml(detail.symptoms[0]?.duration || 'No indicada')}</p>
      <p><strong>Examen:</strong> ${escapeHtml(detail.examinations[0]?.name || 'No indicado')} ${escapeHtml(detail.examinations[0]?.value || '')} ${escapeHtml(detail.examinations[0]?.unit || '')}</p>
      <p><strong>Triaje:</strong> ${escapeHtml(detail.triage?.urgency || 'No disponible')}</p>`;

    evidence.innerHTML = detail.evidence?.map(item => `
      <article><strong>${escapeHtml(item.title)}</strong><br>
      Fuente: ${escapeHtml(item.source)}<br>
      <small>${escapeHtml(item.excerpt)}</small></article>`).join('') || '<p>No hay evidencia disponible.</p>';
  } catch (error) {
    status.textContent = `Error: ${error.message}`;
  }
});
