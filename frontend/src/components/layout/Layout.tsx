import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
    FolderOpen,
    Plus,
    ChevronRight
} from 'lucide-react'
import { Logo } from '../common/Logo'

interface LayoutProps {
    children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
    const location = useLocation()

    const navigation = [
        { name: 'Projects', href: '/projects', icon: FolderOpen },
        { name: 'New Project', href: '/projects/new', icon: Plus },
    ]

    return (
        <div className="h-screen overflow-hidden flex bg-gray-50/50">
            {/* Sidebar */}
            <aside className="w-72 bg-gradient-to-b from-slate-900 via-rose-950/20 to-slate-900 flex flex-col shadow-2xl z-20 backdrop-blur-sm border-r border-white/5">
                {/* Logo */}
                <div className="p-8 border-b border-white/5">
                    <Link to="/" className="flex items-center gap-4 group">
                        <Logo className="w-12 h-12 transition-transform duration-500 group-hover:scale-105" />
                    </Link>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-6 space-y-3 overflow-y-auto">
                    {navigation.map((item) => {
                        const isActive = location.pathname === item.href ||
                            (item.href !== '/' && location.pathname.startsWith(item.href))

                        return (
                            <Link
                                key={item.name}
                                to={item.href}
                                className={`
                  flex items-center gap-4 px-5 py-4 rounded-2xl transition-all duration-300 group
                  ${isActive
                                        ? 'bg-gradient-to-r from-rose-600 to-orange-600 text-white font-semibold shadow-lg shadow-rose-900/20'
                                        : 'text-slate-400 hover:bg-white/5 hover:text-white'}
                `}
                            >
                                <item.icon className={`w-5 h-5 transition-transform duration-300 ${isActive ? 'scale-110' : 'group-hover:scale-110'}`} />
                                <span className="font-medium">{item.name}</span>
                                {isActive && <ChevronRight className="w-4 h-4 ml-auto text-white/50" />}
                            </Link>
                        )
                    })}
                </nav>

                {/* Footer (No Settings) */}
                <div className="p-6 border-t border-white/5">
                    <div className="text-center">
                        <p className="text-[10px] text-slate-500 font-medium uppercase tracking-widest">Powered by AI</p>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 h-full overflow-y-auto w-full relative">
                {/* Background Decor */}
                <div className="fixed top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
                    <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] bg-rose-500/10 rounded-full blur-[120px]" />
                    <div className="absolute bottom-[-10%] left-[20%] w-[500px] h-[500px] bg-orange-500/10 rounded-full blur-[100px]" />
                </div>

                <div className="relative z-10 max-w-7xl mx-auto p-8 lg:p-12 pb-32">
                    {children}
                </div>
            </main>
        </div>
    )
}
