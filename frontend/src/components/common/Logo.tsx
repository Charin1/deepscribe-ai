import React from 'react';

interface LogoProps {
    className?: string;
    showText?: boolean;
    textClassName?: string;
    subTextClassName?: string;
}

export const Logo: React.FC<LogoProps> = ({
    className = "w-10 h-10",
    showText = true,
    textClassName = "text-2xl font-bold text-white tracking-tight",
    subTextClassName = "text-xs text-rose-200 font-bold tracking-wide opacity-80"
}) => {
    return (
        <div className="flex items-center gap-3">
            <div className={`relative ${className} flex items-center justify-center`}>
                <div className="absolute inset-0 bg-gradient-to-br from-rose-500 to-orange-500 rounded-xl blur-[2px] opacity-70"></div>

                {/* Logo Container */}
                <div className="relative w-full h-full bg-slate-900 rounded-xl border border-white/10 flex items-center justify-center p-2 shadow-xl overflow-hidden group">

                    {/* Circuit Background Pattern */}
                    <svg className="absolute inset-0 w-full h-full opacity-20 text-rose-500" viewBox="0 0 100 100" fill="none">
                        <path d="M10 10 h 20 v 20 h -20 z" stroke="currentColor" strokeWidth="0.5" />
                        <path d="M70 70 h 20 v 20 h -20 z" stroke="currentColor" strokeWidth="0.5" />
                        <path d="M30 20 h 40" stroke="currentColor" strokeWidth="0.5" />
                        <path d="M20 30 v 40" stroke="currentColor" strokeWidth="0.5" />
                        <circle cx="50" cy="50" r="30" stroke="currentColor" strokeWidth="0.5" strokeDasharray="4 2" />
                    </svg>

                    {/* Main Icon: Quill + Circuit Integration */}
                    <svg viewBox="0 0 24 24" fill="none" className="w-full h-full text-white drop-shadow-md z-10" xmlns="http://www.w3.org/2000/svg">
                        {/* Quill Shaft - Elegant Curve */}
                        <path d="M19 4C19 4 14.5 4.5 12 9C9.5 13.5 10 21 10 21" stroke="url(#paint0_linear)" strokeWidth="1.5" strokeLinecap="round" />

                        {/* Feather Elements - Stylized */}
                        <path d="M12.5 8.5C11.5 8.5 7 9 7 9" stroke="url(#paint1_linear)" strokeWidth="1.5" strokeLinecap="round" strokeOpacity="0.8" />
                        <path d="M11 11.5C10 11.5 6 12 6 12" stroke="url(#paint1_linear)" strokeWidth="1.5" strokeLinecap="round" strokeOpacity="0.6" />
                        <path d="M10.5 15C9.5 15 7 15.5 7 15.5" stroke="url(#paint1_linear)" strokeWidth="1.5" strokeLinecap="round" strokeOpacity="0.4" />

                        {/* Digital Tip / Circuit Nodes */}
                        <circle cx="10" cy="21" r="1.5" fill="#f43f5e" />
                        <path d="M10 21 L13 23 L16 21" stroke="#fb7185" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" />

                        <defs>
                            <linearGradient id="paint0_linear" x1="19" y1="4" x2="10" y2="21" gradientUnits="userSpaceOnUse">
                                <stop stopColor="#fff" />
                                <stop offset="1" stopColor="#f43f5e" />
                            </linearGradient>
                            <linearGradient id="paint1_linear" x1="12" y1="8" x2="6" y2="12" gradientUnits="userSpaceOnUse">
                                <stop stopColor="#fb7185" />
                                <stop offset="1" stopColor="#f97316" />
                            </linearGradient>
                        </defs>
                    </svg>

                    {/* Animated Sparkle */}
                    <div className="absolute top-2 right-2 w-1.5 h-1.5 bg-white rounded-full animate-pulse shadow-[0_0_8px_rgba(255,255,255,0.8)]"></div>
                </div>
            </div>

            {showText && (
                <div>
                    <h1 className={textClassName}>DeepScribe</h1>
                    <div className="flex items-center gap-1.5">
                        <div className="h-1 w-1 rounded-full bg-emerald-400 animate-pulse" />
                        <p className={subTextClassName}>AI CONTENT STUDIO</p>
                    </div>
                </div>
            )}
        </div>
    );
};
