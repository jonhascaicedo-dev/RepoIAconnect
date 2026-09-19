const form = document.getElementById('case-form');
const result = document.getElementById('result');
const output = document.getElementById('output');

function parseSymptoms(value) {
  return value.split(',').map(x => x.trim()).filter(Boolean).map(name => ({name}));
}

function parseExaminations(value) {
  return value.split(',').map(x => x.trim()).filter(Boolean).map(raw => {
    const [name, valuePart] = raw.split('=').map(x => x.trim());
    return {name, value: valuePart ?? null};
  });
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  output.textContent = 'Procesando...';
  result.hidden = false;
  try {
    const response = await fetch('/api/cases', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        patient_id: document.getElementById('patient-id').value.trim(),
        symptoms: parseSymptoms(document.getElementById('symptoms').value),
        examinations: parseExaminations(document.getElementById('examinations').value)
      })
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.detail || 'Error en la API');
    const detail = await fetch(`/api/cases/${body.case_id}`);
    output.textContent = JSON.stringify(await detail.json(), null, 2);
  } catch (error) {
    output.textContent = `Error: ${error.message}`;
  }
});
