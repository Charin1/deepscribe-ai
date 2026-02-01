import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
    FolderOpen,
    Plus,
    Settings,
    ChevronRight
} from 'lucide-react'

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
        <div className="min-h-screen flex">
            {/* Sidebar */}
            <aside className="w-64 bg-red-600 flex flex-col shadow-xl">
                {/* Logo */}
                <div className="p-6 border-b border-red-500">
                    <Link to="/" className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-white p-1.5 shadow-lg flex items-center justify-center">
                            <span className="text-2xl">🚀</span>
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-white tracking-tight">DeepScribe</h1>
                            <p className="text-xs text-red-100 font-medium opacity-90">AI Content Studio</p>
                        </div>
                    </Link>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-4 space-y-2">
                    {navigation.map((item) => {
                        const isActive = location.pathname === item.href ||
                            (item.href !== '/' && location.pathname.startsWith(item.href))

                        return (
                            <Link
                                key={item.name}
                                to={item.href}
                                className={`
                  flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300
                  ${isActive
                                        ? 'bg-white text-red-600 font-semibold shadow-md'
                                        : 'text-white/90 hover:bg-red-500 hover:text-white'}
                `}
                            >
                                <item.icon className="w-5 h-5" />
                                <span className="font-medium">{item.name}</span>
                                {isActive && <ChevronRight className="w-4 h-4 ml-auto" />}
                            </Link>
                        )
                    })}
                </nav>

                {/* Footer */}
                <div className="p-4 border-t border-red-500">
                    <button className="flex items-center gap-3 px-4 py-3 w-full text-white/80 hover:text-white hover:bg-red-500 rounded-xl transition-all">
                        <Settings className="w-5 h-5" />
                        <span className="font-medium">Settings</span>
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                <div className="max-w-6xl mx-auto p-8">
                    {children}
                </div>
            </main>
        </div>
    )
}
