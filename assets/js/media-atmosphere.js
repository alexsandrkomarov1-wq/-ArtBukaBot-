(() => {
  "use strict";

  const root = document.querySelector("[data-media-atmosphere]");
  if (!root) return;

  const scene = root.querySelector("[data-nature-scene]");
  const status = root.querySelector("[data-atmosphere-status]");
  const soundToggle = root.querySelector("[data-sound-toggle]");
  const voiceButton = root.querySelector("[data-voice-assistant]");
  const sceneButtons = [...root.querySelectorAll("[data-scene-choice]")];
  const moodButtons = [...root.querySelectorAll("[data-mood-choice]")];

  const scenes = ["forest", "lake", "mountain", "sunset"];
  const sceneNames = { forest: "Лес", lake: "Озеро", mountain: "Горы", sunset: "Закат" };
  const moodNames = { romance: "Романтика", calm: "Спокойствие", focus: "Фокус", nature: "Звуки природы" };
  const progressions = {
    romance: [[261.63, 329.63, 392.00, 523.25], [220.00, 261.63, 329.63, 440.00], [174.61, 220.00, 261.63, 349.23], [196.00, 246.94, 293.66, 392.00]],
    calm: [[196.00, 246.94, 293.66, 392.00], [174.61, 220.00, 261.63, 349.23], [146.83, 196.00, 220.00, 293.66], [164.81, 207.65, 246.94, 329.63]],
    focus: [[220.00, 277.18, 329.63], [196.00, 246.94, 293.66], [246.94, 311.13, 369.99], [220.00, 277.18, 329.63]],
    nature: [[174.61, 261.63, 349.23], [196.00, 293.66, 392.00], [164.81, 246.94, 329.63], [196.00, 261.63, 392.00]]
  };

  let currentScene = "forest";
  let currentMood = "romance";
  let audioContext = null;
  let master = null;
  let playing = false;
  let step = 0;
  let musicTimer = null;
  let sceneTimer = null;
  let recognition = null;

  function setScene(name) {
    if (!scenes.includes(name)) return;
    currentScene = name;
    scene.dataset.natureScene = name;
    sceneButtons.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.sceneChoice === name)));
  }

  function say(text) {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "ru-RU";
    utterance.rate = 0.96;
    utterance.volume = 0.75;
    window.speechSynthesis.speak(utterance);
  }

  function setMood(name) {
    if (!progressions[name]) return;
    currentMood = name;
    moodButtons.forEach(button => {
      button.setAttribute("aria-pressed", String(button.dataset.moodChoice === name));
    });
    status.textContent = "Настроение: " + moodNames[name] + ". " + (playing ? "Музыка уже переключается." : "Нажмите «Включить музыку» или скажите команду.");
  }

  function audio() {
    if (!audioContext) {
      const AudioCtor = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtor) throw new Error("Этот браузер не поддерживает Web Audio.");
      audioContext = new AudioCtor();
      master = audioContext.createGain();
      master.gain.value = 0.0001;
      master.connect(audioContext.destination);
    }
    if (audioContext.state === "suspended") void audioContext.resume();
  }

  function note(frequency, start, duration, volume, type) {
    const oscillator = audioContext.createOscillator();
    const envelope = audioContext.createGain();
    oscillator.type = type || "sine";
    oscillator.frequency.setValueAtTime(frequency, start);
    envelope.gain.setValueAtTime(0.0001, start);
    envelope.gain.exponentialRampToValueAtTime(Math.max(0.0002, volume), start + 0.45);
    envelope.gain.exponentialRampToValueAtTime(0.0001, start + duration);
    oscillator.connect(envelope);
    envelope.connect(master);
    oscillator.start(start);
    oscillator.stop(start + duration + 0.05);
  }

  function playBar() {
    if (!playing || !audioContext) return;
    const now = audioContext.currentTime + 0.08;
    const chord = progressions[currentMood][step % progressions[currentMood].length];
    const padVolume = currentMood === "focus" ? 0.018 : 0.024;
    chord.forEach((frequency, index) => {
      note(frequency, now + index * 0.035, 3.7, padVolume / (index === 0 ? 1 : 1.35), "sine");
    });
    if (currentMood !== "nature") {
      const melody = chord[(step + 1) % chord.length] * 2;
      note(melody, now + 1.15, 1.65, currentMood === "romance" ? 0.012 : 0.007, "triangle");
      if (currentMood === "romance") note(chord[0] * 3, now + 2.25, 1.1, 0.0045, "sine");
    } else {
      note(659.25, now + 1.4, 2.2, 0.003, "sine");
    }
    step += 1;
    musicTimer = window.setTimeout(playBar, 2900);
  }

  async function startMusic() {
    try {
      audio();
      await audioContext.resume();
      playing = true;
      master.gain.cancelScheduledValues(audioContext.currentTime);
      master.gain.setTargetAtTime(0.72, audioContext.currentTime, 0.9);
      window.clearTimeout(musicTimer);
      soundToggle.textContent = "Ⅱ Выключить музыку";
      status.textContent = "Играет оригинальная фоновая композиция: " + moodNames[currentMood] + ".";
      playBar();
    } catch (error) {
      status.textContent = error.message;
    }
  }

  function stopMusic() {
    playing = false;
    window.clearTimeout(musicTimer);
    if (audioContext && master) {
      master.gain.cancelScheduledValues(audioContext.currentTime);
      master.gain.setTargetAtTime(0.0001, audioContext.currentTime, 0.45);
    }
    soundToggle.textContent = "▶ Включить музыку";
    status.textContent = "Музыка выключена. Природная сцена продолжает меняться.";
  }

  function applyCommand(transcript) {
    const command = transcript.toLowerCase().replace(/ё/g, "е");
    if (/выключи|останови|тишина|без музыки/.test(command)) {
      stopMusic();
      say("Музыка выключена.");
      return;
    }
    const mood = command.includes("романтик") ? "romance"
      : command.includes("спокой") || command.includes("релакс") ? "calm"
      : command.includes("фокус") || command.includes("работ") ? "focus"
      : command.includes("природ") || command.includes("птиц") ? "nature" : null;
    const requestedScene = command.includes("лес") ? "forest"
      : command.includes("озер") || command.includes("море") ? "lake"
      : command.includes("гор") ? "mountain"
      : command.includes("закат") || command.includes("вечер") ? "sunset" : null;
    if (requestedScene) setScene(requestedScene);
    if (mood) {
      setMood(mood);
      void startMusic();
      say("Включаю атмосферу: " + moodNames[mood].toLowerCase() + ".");
    } else if (/включи музыку|начни музыку|играй/.test(command)) {
      void startMusic();
      say("Музыка включена.");
    } else if (requestedScene) {
      say("Меняю пейзаж: " + sceneNames[requestedScene].toLowerCase() + ".");
    } else {
      status.textContent = "Команда не распознана: " + transcript;
      say("Не расслышала команду. Попробуйте сказать: включи романтику.");
    }
  }

  function listen() {
    try {
      audio();
      void audioContext.resume();
    } catch (_) {}
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      status.textContent = "Голосовое управление недоступно в этом браузере. Используйте кнопки настроения.";
      return;
    }
    if (recognition) {
      try { recognition.abort(); } catch (_) {}
    }
    recognition = new SpeechRecognition();
    recognition.lang = "ru-RU";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    voiceButton.disabled = true;
    voiceButton.textContent = "Слушаю…";
    status.textContent = "Слушаю команду. Например: «включи романтику» или «покажи озеро».";
    recognition.onresult = event => applyCommand(event.results[0][0].transcript);
    recognition.onerror = event => {
      status.textContent = "Голосовое управление: " + (event.error || "ошибка распознавания") + ". Можно воспользоваться кнопками.";
    };
    recognition.onend = () => {
      voiceButton.disabled = false;
      voiceButton.textContent = "🎙 Голосовой помощник";
    };
    try {
      recognition.start();
    } catch (error) {
      voiceButton.disabled = false;
      voiceButton.textContent = "🎙 Голосовой помощник";
      status.textContent = "Не удалось запустить микрофон: " + error.message;
    }
  }

  sceneButtons.forEach(button => button.addEventListener("click", () => setScene(button.dataset.sceneChoice)));
  moodButtons.forEach(button => button.addEventListener("click", () => {
    setMood(button.dataset.moodChoice);
    void startMusic();
  }));
  soundToggle.addEventListener("click", () => playing ? stopMusic() : void startMusic());
  voiceButton.addEventListener("click", listen);

  sceneTimer = window.setInterval(() => {
    if (document.hidden) return;
    const next = (scenes.indexOf(currentScene) + 1) % scenes.length;
    setScene(scenes[next]);
  }, 18000);

  window.addEventListener("pagehide", () => {
    window.clearInterval(sceneTimer);
    window.clearTimeout(musicTimer);
    if (recognition) {
      try { recognition.abort(); } catch (_) {}
    }
    if (audioContext && audioContext.state !== "closed") void audioContext.close();
  });
})();