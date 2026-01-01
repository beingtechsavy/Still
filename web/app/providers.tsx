'use client';

import { RitualProvider } from './context/RitualContext';

export function Providers({ children }: { children: React.ReactNode }) {
    return (
        <RitualProvider>
            {children}
        </RitualProvider>
    );
}
