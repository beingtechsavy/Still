'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useRitual } from '../context/RitualContext';

export default function AudioRecorder() {
    const [permission, setPermission] = useState<PermissionState>('prompt');
    const [isRecording, setIsRecording] = useState(false);
    const [timeLeft, setTimeLeft] = useState(90);
    const mediaRecorder = useRef<MediaRecorder | null>(null);
    const chunks = useRef<Blob[]>([]);
    const router = useRouter();
    const { setAudioBlob } = useRitual();

    useEffect(() => {
        // Check initial permission status if possible (broadly supported)
        if (navigator.permissions && navigator.permissions.query) {
            navigator.permissions.query({ name: 'microphone' as PermissionName })
                .then((status) => {
                    setPermission(status.state);
                });
        }
    }, []);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            setPermission('granted');

            const mimeType = MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : "audio/mp4";
            const options = MediaRecorder.isTypeSupported(mimeType) ? { mimeType } : undefined;

            mediaRecorder.current = new MediaRecorder(stream, options);
            chunks.current = [];

            mediaRecorder.current.ondataavailable = (e) => {
                if (e.data.size > 0) chunks.current.push(e.data);
            };

            mediaRecorder.current.onstop = () => {
                const type = options?.mimeType || 'audio/webm';
                const fullBlob = new Blob(chunks.current, { type });
                console.log('Recording finished, blob size:', fullBlob.size, 'type:', type);

                // Save to context
                setAudioBlob(fullBlob);

                router.push('/pause');
            };

            mediaRecorder.current.start();
            setIsRecording(true);
        } catch (err) {
            console.error('Microphone access denied:', err);
            setPermission('denied');
        }
    };

    const stopRecording = () => {
        if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
            mediaRecorder.current.stop();
            setIsRecording(false);
            mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
        }
    };

    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (isRecording && timeLeft > 0) {
            interval = setInterval(() => {
                setTimeLeft((prev) => prev - 1);
            }, 1000);
        } else if (timeLeft === 0 && isRecording) {
            stopRecording();
        }
        return () => clearInterval(interval);
    }, [isRecording, timeLeft]);

    return (
        <div className="flex flex-col items-center justify-center space-y-12 fade-in w-full h-full">
            {/* Timer / Status Display */}
            <div className="text-center space-y-2">
                {isRecording ? (
                    <div className="text-4xl font-light text-white/90 tabular-nums">
                        {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}
                    </div>
                ) : (
                    <div className="text-xl text-white/60">
                        {permission === 'denied'
                            ? "Microphone access is needed."
                            : "Speak your mind."}
                    </div>
                )}
            </div>

            {/* Control Button - Abstract Circle Design */}
            <button
                onClick={isRecording ? stopRecording : startRecording}
                className={`
          w-24 h-24 rounded-full border transition-all duration-700 ease-in-out flex items-center justify-center
          ${isRecording
                        ? 'border-white/80 bg-white/5 scale-110'
                        : 'border-white/20 hover:border-white/50 bg-transparent'}
        `}
                aria-label={isRecording ? "Stop Recording" : "Start Recording"}
            >
                <div className={`
          rounded-full transition-all duration-700
          ${isRecording
                        ? 'w-4 h-4 bg-white/80 rounded-sm' // Stop icon (square-ish)
                        : 'w-16 h-16 bg-white/0 hover:bg-white/5'} // Ambient touch target
        `} />
            </button>

            {/* Guide text */}
            <div className="h-4 text-sm text-white/30 text-center font-light">
                {isRecording ? "Tap to finish early" : "Tap the circle to begin"}
            </div>
        </div>
    );
}
