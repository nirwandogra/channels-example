let recorder;
const recordAudio = () =>
  new Promise(async resolve => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    const audioChunks = [];

    mediaRecorder.addEventListener("dataavailable", event => {
      audioChunks.push(event.data);
    });

    const start = () => mediaRecorder.start();

    const stop = () =>
      new Promise(resolve => {
        mediaRecorder.addEventListener("stop", () => {
          const audioBlob = new Blob(audioChunks);
          const audioUrl = URL.createObjectURL(audioBlob);
          const audio = new Audio(audioUrl);
          const play = () => audio.play();
          console.log(audioBlob);
          console.log(audioUrl);
          resolve({ audioBlob, audioUrl, play });
        });

        mediaRecorder.stop();
      });

    resolve({ start, stop });
  });

const sleep = time => new Promise(resolve => setTimeout(resolve, time));

const startRecording = async () => {
  recorder = await recordAudio();
  const actionButton = document.getElementById('action');
  actionButton.disabled = true;
  recorder.start();
}

const stopRecording = async () => {
  const audio = await recorder.stop();
  const actionButton = document.getElementById('action');
  audio.play();
  await sleep(3000);
  actionButton.disabled = false;
}
