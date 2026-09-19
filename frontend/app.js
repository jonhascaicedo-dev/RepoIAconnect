const form = document.getElementById('case-form');
const result = document.getElementById('result');
const summary = document.getElementById('summary');
const status = document.getElementById('status');
const hypotheses = document.getElementById('hypotheses');
const evidence = document.getElementById('evidence');

const severityLabels = { mild: 'Leve', moderate: 'Moderada', severe: 'Fuerte' };
const urgencyLabels = { not_assessed: 'Pendiente de evaluación clínica' };
const processingLabels = { processing: 'Procesando consulta…', ai_review: 'Análisis de IA en revisión…', completed: 'Análisis completado', failed: 'Error de procesamiento' };

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>\"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#039;'}[ch]));
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  result.hidden = false;
  status.textContent = 'Procesando consulta…';
  summary.textContent = '';
  hypotheses.textContent = '';
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

    status.textContent = processingLabels[detail.status] || 'Estado del procesamiento: no disponible';
    const symptomDetail = detail.symptoms[0] || {};
    const examDetail = detail.examinations[0] || {};
    const urgency = detail.triage?.urgency;

    summary.innerHTML = `
      <p><strong>Caso:</strong> ${escapeHtml(detail.id)}</p>
      <p><strong>Síntoma:</strong> ${escapeHtml(symptomDetail.name)}</p>
      <p><strong>Intensidad:</strong> ${escapeHtml(severityLabels[symptomDetail.severity] || 'No indicada')}</p>
      <p><strong>Duración:</strong> ${escapeHtml(symptomDetail.duration || 'No indicada')}</p>
      <p><strong>Examen:</strong> ${escapeHtml(examDetail.name || 'No indicado')} ${escapeHtml(examDetail.value || '')} ${escapeHtml(examDetail.unit || '')}</p>
      <p><strong>Triaje:</strong> ${escapeHtml(urgencyLabels[urgency] || 'No disponible')}</p>`;

    hypotheses.innerHTML = detail.hypotheses?.map(item => `
      <article><strong>${escapeHtml(item.name)}</strong>
      <p><strong>Confianza:</strong> No calculada en el proveedor sintético.</p>
      <p><strong>Información faltante:</strong> ${escapeHtml((item.missing_information || []).join(', '))}</p></article>`).join('') || '<p>No hay hipótesis disponibles.</p>';

    evidence.innerHTML = detail.evidence?.map(item => `
      <article><strong>${escapeHtml(item.title)}</strong><br>
      Fuente: ${escapeHtml(item.source)}<br>
      <small>${escapeHtml(item.excerpt)}</small></article>`).join('') || '<p>No hay evidencia disponible.</p>';
  } catch (error) {
    status.textContent = `Error: ${error.message}`;
  }
});
