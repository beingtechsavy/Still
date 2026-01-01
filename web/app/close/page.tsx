import Link from 'next/link';

export default function ClosePage() {
    return (
        <div className="flex-1 flex flex-col justify-center items-center fade-in space-y-8 text-center">
            <p className="text-xl text-white/80 font-serif italic">
                "Gone."
            </p>

            <p className="text-sm text-white/30 max-w-xs leading-relaxed">
                The audio is deleted.<br />
                The text is deleted.<br />
                Only this memory remains.
            </p>

            <div className="pt-12">
                <Link
                    href="/"
                    className="w-12 h-12 rounded-full border border-white/10 hover:border-white/40 flex items-center justify-center transition-all duration-500"
                    aria-label="Return home"
                >
                    <div className="w-1 h-1 bg-white/40 rounded-full" />
                </Link>
            </div>
        </div>
    );
}
