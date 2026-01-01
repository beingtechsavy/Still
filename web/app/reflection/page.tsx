'use client';

import Link from 'next/link';
import { useRitual } from '../context/RitualContext';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function ReflectionPage() {
    const { reflectionData } = useRitual();
    const router = useRouter();

    useEffect(() => {
        if (!reflectionData) {
            // Optional: redirect if accessed directly
            // router.push('/');
        }
    }, [reflectionData, router]);

    const data = reflectionData || {
        reflection: "Silence is also an answer.", // ✅ FIXED
        flashcard: {
            title: "Stillness",
            bullets: ["..."]
        },
        confidence: 0
    };

    return (
        // <div className="flex-1 flex flex-col justify-center items-start fade-in space-y-12">
        //     <div className="space-y-6">
        //         <h2 className="text-xl text-white/80 font-serif leading-relaxed">
        //             {data.reflection}
        //         </h2>
        //     </div>

        //     <div className="w-full border-t border-white/10 pt-8 space-y-4">
        //         <h3 className="text-xs font-sans uppercase tracking-widest text-white/40">
        //             The Truths
        //         </h3>
        //         <ul className="space-y-3">
        //             {data.flashcard.bullets.map((bullet, i) => (
        //                 <li
        //                     key={i}
        //                     className="text-sm text-white/60 font-light leading-normal pl-4 border-l border-white/10"
        //                 >
        //                     {bullet}
        //                 </li>
        //             ))}
        //         </ul>
        //     </div>

        //     <div className="pt-8">
        //         <Link
        //             href="/close"
        //             className="text-white/40 hover:text-white/80 text-sm transition-colors duration-300"
        //         >
        //             Close this moment &rarr;
        //         </Link>
        //     </div>
        // </div>




    <div className="flex-1 flex flex-col fade-in h-full">
    {/* Scrollable content */}
    <div className="flex-1 overflow-y-auto no-scrollbar pr-1">
      <div className="space-y-12 pb-24">
        {/* Reflection text */}
        <div className="space-y-6">
          <h2 className="text-xl text-white/80 font-serif leading-relaxed">
            {data.reflection}
          </h2>
        </div>

        {/* Flashcard */}
        <div className="w-full border-t border-white/10 pt-8 space-y-4">
          <h3 className="text-xs font-sans uppercase tracking-widest text-white/40">
            The Truths
          </h3>
          <ul className="space-y-3">
            {data.flashcard.bullets.map((bullet, i) => (
              <li
                key={i}
                className="text-sm text-white/60 font-light leading-normal pl-4 border-l border-white/10"
              >
                {bullet}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>

    {/* Fixed bottom action */}
    <div className="pt-6">
      <Link
        href="/close"
        className="text-white/40 hover:text-white/80 text-sm transition-colors duration-300"
      >
        Close this moment →
      </Link>
    </div>
  </div>    
    );
}
