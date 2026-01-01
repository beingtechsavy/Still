// 'use client';

// import { useEffect, useState } from 'react';
// import { useRouter } from 'next/navigation';
// import { useRitual } from '../context/RitualContext';

// export default function PausePage() {
//     const router = useRouter();
//     const { audioBlob, setReflectionData, setAudioBlob } = useRitual();
//     const [pulse, setPulse] = useState(false);

//     useEffect(() => {
//         const processReflection = async () => {
//             if (!audioBlob) {
//                 console.warn("No audio payload found. Waiting...");
//                 // router.replace('/');
//                 return;
//             }

//             // Start breathing animation
//             setPulse(true);

//             try {
//                 const formData = new FormData();
//                 formData.append('file', audioBlob, 'recording.webm');

//                 const apiUrl =
//                     process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

//                 const response = await fetch(`${apiUrl}/process-audio`, {
//                     method: 'POST',
//                     body: formData,
//                 });

//                 if (!response.ok) {
//                     throw new Error(`API Error: ${response.status}`);
//                 }

//                 const data = await response.json();
//                 console.log("Reflection received:", data);

//                 // ✅ Set reflection first
//                 setReflectionData(data);

//                 // ✅ Clear audio so next run is clean
//                 setAudioBlob(null);

//                 // ✅ Navigate ONLY after state is set
//                 router.replace('/reflection');

//             } catch (err) {
//                 console.error("Reflection failed:", err);

//                 // ✅ Graceful guaranteed fallback
//                 setReflectionData({
//                     reflection:
//                         "You spoke about something that has been weighing on you, and even getting it out like this took effort. What you were carrying does not say anything about your ability or your worth, only about the strain of facing the same limits again and again. This moment does not need to resolve that struggle or turn it into meaning. You don’t need to keep carrying this version of the year forward.",
//                     flashcard: {
//                         title: "Still Heard",
//                         bullets: [
//                             "Effort was made",
//                             "Weight acknowledged",
//                             "Permission to stop"
//                         ]
//                     },
//                     confidence: 0
//                 });

//                 router.replace('/reflection');
//             }
//         };

//         processReflection();
//     }, [audioBlob, router, setReflectionData, setAudioBlob]);

//     return (
//         <div className="flex-1 flex flex-col items-center justify-center space-y-8 fade-in h-full">
//             <div
//                 className={`w-2 h-2 rounded-full bg-white/40 transition-all duration-[3000ms] ease-in-out ${
//                     pulse ? 'opacity-80 scale-150' : 'opacity-20 scale-100'
//                 }`}
//             />
//             <p className="text-sm text-white/30 font-light tracking-widest uppercase">
//                 Reflecting
//             </p>
//         </div>
//     );
// }



'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useRitual } from '../context/RitualContext';

export default function PausePage() {
  const router = useRouter();
  const { audioBlob, setReflectionData, setAudioBlob } = useRitual();
  const [pulse, setPulse] = useState(false);

  // 🔒 Execution lock (prevents double API calls)
  const hasProcessedRef = useRef(false);

  useEffect(() => {
    if (!audioBlob) return;
    if (hasProcessedRef.current) return;

    hasProcessedRef.current = true;

    const processReflection = async () => {
      setPulse(true);

      try {
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.webm');

        const apiUrl =
          process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

        const response = await fetch(`${apiUrl}/process-audio`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();

        setReflectionData(data);
        setAudioBlob(null);

        router.push('/reflection');
      } catch (err) {
        console.error('Reflection failed:', err);

        setReflectionData({
          reflection:
            'You spoke, and for now that is enough. This moment does not need to carry anything further.',
          flashcard: {
            title: 'Still',
            bullets: ['Spoken', 'Received', 'Released'],
          },
          confidence: 0.1,
        });

        router.push('/reflection');
      }
    };

    processReflection();
  }, [audioBlob, router, setReflectionData, setAudioBlob]);

  return (
    <div className="flex-1 flex flex-col items-center justify-center fade-in h-full">
    {/* Ripple container */}
    <div className="relative w-24 h-24 flex items-center justify-center">
      <div className="ripple" />
      <div className="ripple delay" />
      <div className="ripple delay-2" />

      {/* Center point */}
      <div className="w-2 h-2 rounded-full bg-white/60 z-10" />
    </div>

    <p className="mt-10 text-xs text-white/30 font-light tracking-widest uppercase">
      Reflecting
    </p>
  </div>
  );
}
