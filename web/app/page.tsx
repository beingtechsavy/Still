import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex-1 flex flex-col justify-center items-start fade-in space-y-12">
      <header className="space-y-4">
        <h1 className="text-3xl font-serif tracking-tight text-white/90">
          Still.
        </h1>
        <p className="text-lg text-white/60 leading-relaxed max-w-xs">
          This is not an app.<br />
          This is a ritual.
        </p>
      </header>

      <div className="space-y-8">
        <p className="text-base text-white/40 leading-relaxed font-light">
          Everything is anonymous.<br />
          Nothing is saved.<br />
          Just speak, and let go.
        </p>
      </div>

      <div className="pt-12">
        <Link
          href="/speak"
          className="text-xl text-white/90 border-b border-white/20 pb-1 hover:border-white/60 transition-colors duration-500 ease-in-out"
        >
          Begin
        </Link>
      </div>
    </div>
  );
}
