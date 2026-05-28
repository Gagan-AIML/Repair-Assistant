const { createApp, ref, computed, nextTick, onMounted } = Vue;

const HISTORY_KEY = 'repairai_history';

createApp({
  setup() {
    // ── STATE ──────────────────────────────────────────────
    const userIssue     = ref('');
    const imageFile     = ref(null);
    const imagePreview  = ref(null);
    const isDragging    = ref(false);
    const isLoading     = ref(false);
    const loadStep      = ref(0);
    const results       = ref(null);
    const error         = ref(null);
    const sidebarOpen   = ref(false);
    const history       = ref([]);
    const currentSaved  = ref(false);
    const activeHistoryId = ref(null);

    // Chat
    const chatQuestion  = ref('');
    const chatMessages  = ref([]);
    const chatLoading   = ref(false);
    const chatBox       = ref(null);

    // ── COMPUTED ───────────────────────────────────────────
    const hasOcr = computed(() =>
      results.value?.ocr_context &&
      results.value.ocr_context !== 'No image provided.' &&
      !results.value.ocr_context.startsWith('OCR Extraction unavailable')
    );
    const hasVision = computed(() =>
      results.value?.vision_analysis &&
      results.value.vision_analysis !== 'No image provided. Diagnosis based on text description only.'
    );
    const ocrLines = computed(() =>
      (results.value?.ocr_context || '').split('\n').filter(l => l.trim())
    );

    // ── MARKDOWN RENDERER ──────────────────────────────────
    const md = (text) => {
      if (!text) return '';
      return marked.parse(text);
    };

    // ── IMAGE HANDLING ─────────────────────────────────────
    const onFileChange = (e) => {
      const file = e.target.files[0];
      if (file) setImage(file);
    };
    const onDrop = (e) => {
      isDragging.value = false;
      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith('image/')) setImage(file);
    };
    const setImage = (file) => {
      imageFile.value = file;
      const reader = new FileReader();
      reader.onload = (e) => { imagePreview.value = e.target.result; };
      reader.readAsDataURL(file);
    };
    const clearImage = () => {
      imageFile.value = null;
      imagePreview.value = null;
      document.getElementById('fileInput').value = '';
    };

    // ── DIAGNOSIS ──────────────────────────────────────────
    let loadStepTimer = null;
    const runDiagnosis = async () => {
      if (!userIssue.value.trim()) return;
      isLoading.value = true;
      error.value = null;
      results.value = null;
      currentSaved.value = false;
      chatMessages.value = [];
      loadStep.value = 0;

      // Animate loading steps
      const steps = [0, 1, 2, 3];
      let i = 0;
      loadStepTimer = setInterval(() => {
        if (i < steps.length - 1) { i++; loadStep.value = i; }
      }, 1800);

      const formData = new FormData();
      formData.append('user_issue', userIssue.value);
      if (imageFile.value) formData.append('image', imageFile.value);

      try {
        const res = await fetch('/api/diagnose', { method: 'POST', body: formData });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || 'Diagnosis failed');
        }
        results.value = await res.json();
        loadStep.value = 4;
      } catch (e) {
        error.value = e.message;
        isLoading.value = false;
      } finally {
        clearInterval(loadStepTimer);
        isLoading.value = false;
      }
    };

    // ── RESET ──────────────────────────────────────────────
    const resetAll = () => {
      results.value = null;
      error.value = null;
      userIssue.value = '';
      clearImage();
      chatMessages.value = [];
      chatQuestion.value = '';
      currentSaved.value = false;
      activeHistoryId.value = null;
    };

    // ── CHAT ───────────────────────────────────────────────
    const sendChat = async () => {
      if (!chatQuestion.value.trim() || chatLoading.value) return;
      const question = chatQuestion.value.trim();
      chatQuestion.value = '';

      const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      chatMessages.value.push({ id: Date.now(), role: 'user', text: question, time: now });
      await scrollChat();

      chatLoading.value = true;

      // Build chat history string
      const histStr = chatMessages.value
        .map(m => `${m.role === 'user' ? 'User' : 'Assistant'}: ${m.text}`)
        .join('\n');

      const formData = new FormData();
      formData.append('user_question', question);
      formData.append('original_issue', userIssue.value);
      formData.append('causes',   results.value?.sections?.causes || '');
      formData.append('fixes',    results.value?.sections?.fixes || '');
      formData.append('verdict',  results.value?.sections?.verdict || '');
      formData.append('tips',     results.value?.sections?.tips || '');
      formData.append('vision_analysis',    results.value?.vision_analysis || '');
      formData.append('ocr_context',        results.value?.ocr_context || '');
      formData.append('detected_components', (results.value?.detected_components || []).join(', '));
      formData.append('chat_history', histStr);

      try {
        const res = await fetch('/api/chat', { method: 'POST', body: formData });
        if (!res.ok) { const e = await res.json(); throw new Error(e.detail); }
        const data = await res.json();
        chatMessages.value.push({
          id: Date.now() + 1, role: 'assistant', text: data.answer,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });
      } catch (e) {
        chatMessages.value.push({
          id: Date.now() + 1, role: 'assistant',
          text: `⚠️ Chat error: ${e.message}`, time: ''
        });
      } finally {
        chatLoading.value = false;
        await scrollChat();
      }
    };

    const askSuggestion = (q) => {
      chatQuestion.value = q;
      sendChat();
    };

    const scrollChat = async () => {
      await nextTick();
      if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight;
    };

    // ── HISTORY ────────────────────────────────────────────
    const loadStoredHistory = () => {
      try {
        const raw = localStorage.getItem(HISTORY_KEY);
        history.value = raw ? JSON.parse(raw) : [];
      } catch { history.value = []; }
    };

    const persistHistory = () => {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(history.value));
    };

    const saveToHistory = () => {
      if (!results.value || currentSaved.value) return;
      const item = {
        id: Date.now().toString(),
        date: new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }),
        issue: userIssue.value,
        device_type: results.value.device_type,
        is_user_fix: results.value.is_user_fix,
        imagePreview: imagePreview.value,
        results: results.value,
      };
      history.value.unshift(item);
      // Keep max 30 items
      if (history.value.length > 30) history.value = history.value.slice(0, 30);
      persistHistory();
      currentSaved.value = true;
      activeHistoryId.value = item.id;
    };

    const loadHistory = (item) => {
      userIssue.value = item.issue;
      imagePreview.value = item.imagePreview || null;
      imageFile.value = null;
      results.value = item.results;
      chatMessages.value = [];
      currentSaved.value = true;
      activeHistoryId.value = item.id;
      sidebarOpen.value = false;
      error.value = null;
    };

    const deleteHistory = (id) => {
      history.value = history.value.filter(h => h.id !== id);
      persistHistory();
      if (activeHistoryId.value === id) {
        activeHistoryId.value = null;
        currentSaved.value = false;
      }
    };

    const clearAllHistory = () => {
      if (confirm('Clear all saved diagnoses?')) {
        history.value = [];
        localStorage.removeItem(HISTORY_KEY);
        activeHistoryId.value = null;
        currentSaved.value = false;
      }
    };

    // ── INIT ───────────────────────────────────────────────
    onMounted(() => { loadStoredHistory(); });

    return {
      userIssue, imageFile, imagePreview, isDragging,
      isLoading, loadStep, results, error,
      sidebarOpen, history, currentSaved, activeHistoryId,
      chatQuestion, chatMessages, chatLoading, chatBox,
      hasOcr, hasVision, ocrLines,
      md, onFileChange, onDrop, clearImage,
      runDiagnosis, resetAll,
      sendChat, askSuggestion,
      saveToHistory, loadHistory, deleteHistory, clearAllHistory,
    };
  }
}).mount('#app');
