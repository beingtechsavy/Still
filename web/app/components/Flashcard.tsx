'use client';

import { forwardRef } from 'react';

interface FlashcardProps {
    title: string;
    bullets: string[];
    date?: string;
}

export const Flashcard = forwardRef<HTMLDivElement, FlashcardProps>(({ title, bullets, date }, ref) => {
    // Current date if not provided
    const displayDate = date || new Date().toLocaleDateString('en-US', { 
        month: 'long', 
        day: 'numeric', 
        year: 'numeric' 
    });

    return (
        <div 
            ref={ref}
            className="w-[400px] h-[500px] bg-[#0A0A0A] p-8 flex flex-col justify-between border border-white/10 relative overflow-hidden"
            style={{ 
                // Stick to a fixed size for consistent export
                minWidth: '400px', 
                minHeight: '500px'
            }}
        >
            {/* Background Texture/Gradient (Subtle) */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
            
            {/* Header */}
            <div className="z-10 space-y-2">
                <p className="text-xs text-white/30 uppercase tracking-[0.2em]">Still</p>
                <h2 className="text-2xl text-white/90 font-serif italic leading-tight">
                    {title}
                </h2>
            </div>

            {/* Content */}
            <div className="z-10 flex-1 flex flex-col justify-center space-y-6">
                <ul className="space-y-4">
                    {bullets.map((bullet, i) => (
                        <li key={i} className="flex gap-4">
                            <span className="text-white/20 text-sm mt-1">•</span>
                            <span className="text-sm text-white/70 font-light leading-relaxed">
                                {bullet}
                            </span>
                        </li>
                    ))}
                </ul>
            </div>

            {/* Footer */}
            <div className="z-10 pt-8 border-t border-white/10 flex justify-between items-end">
                <span className="text-[10px] text-white/20 uppercase tracking-widest">
                    {displayDate}
                </span>
                <div className="w-2 h-2 rounded-full bg-white/20" />
            </div>
        </div>
    );
});

Flashcard.displayName = 'Flashcard';
