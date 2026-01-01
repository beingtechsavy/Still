'use client';

import { useEffect } from 'react';
import { useRitual } from '../context/RitualContext';
import AudioRecorder from '../components/AudioRecorder';

export default function SpeakPage() {
    const { setReflectionData } = useRitual();

    // 🔑 Clear old reflection when starting a new ritual
    useEffect(() => {
        setReflectionData(null);
    }, [setReflectionData]);

    return (
        <div className="flex-1 flex flex-col items-center justify-center h-full">
            <AudioRecorder />
        </div>
    );
}
