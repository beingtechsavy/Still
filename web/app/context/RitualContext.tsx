'use client';

import { createContext, useContext, useState, ReactNode } from 'react';

interface ReflectionData {
    reflection: string; // ✅ FIXED: matches backend
    flashcard: {
        title: string;
        bullets: string[];
    };
    confidence: number;
}

interface RitualContextType {
    audioBlob: Blob | null;
    setAudioBlob: (blob: Blob | null) => void;
    reflectionData: ReflectionData | null;
    setReflectionData: (data: ReflectionData | null) => void;
}

const RitualContext = createContext<RitualContextType | undefined>(undefined);

export function RitualProvider({ children }: { children: ReactNode }) {
    const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
    const [reflectionData, setReflectionData] = useState<ReflectionData | null>(null);

    return (
        <RitualContext.Provider
            value={{ audioBlob, setAudioBlob, reflectionData, setReflectionData }}
        >
            {children}
        </RitualContext.Provider>
    );
}

export function useRitual() {
    const context = useContext(RitualContext);
    if (context === undefined) {
        throw new Error('useRitual must be used within a RitualProvider');
    }
    return context;
}
