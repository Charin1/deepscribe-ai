import { Link } from 'react-router-dom'
import {
    Sparkles,
    ArrowRight,
    Zap,
    Shield,
    BarChart3,
    Users,
    FileText,
    Search
} from 'lucide-react'

export default function HomePage() {
    const features = [
        {
            icon: Zap,
            title: 'AI-Powered Research',
            description: 'Deep research agents scour the web for authoritative sources and facts.',
        },
        {
            icon: Shield,
            title: 'Quality Validated',
            description: 'Content is reviewed for depth, accuracy, and audience alignment.',
        },
        {
            icon: BarChart3,
            title: 'SEO Optimized',
            description: 'Titles, structure, and content optimized for search engine rankings.',
        },
        {
            icon: Users,
            title: 'Human-in-the-Loop',
            description: 'You control every step - titles, outlines, and final approval.',
        },
    ]

    const workflow = [
        { step: 1, title: 'Define Topic', description: 'Enter your topic, audience, and goals' },
        { step: 2, title: 'Select Title', description: 'Choose from AI-generated SEO titles' },
        { step: 3, title: 'Review Plan', description: 'Edit and approve the content outline' },
        { step: 4, title: 'Watch AI Work', description: 'Real-time agent execution dashboard' },
        { step: 5, title: 'Edit & Publish', description: 'Review, refine, and export' },
    ]

    return (
        <div className="space-y-16">
            {/* Hero Section */}
            <section className="text-center space-y-8 py-12">
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-50 border border-primary-100 rounded-full text-primary-600 text-sm font-medium shadow-sm">
                    <Sparkles className="w-4 h-4" />
                    Powered by CrewAI + Groq
                </div>

                <h1 className="text-5xl md:text-6xl font-bold text-gray-900 leading-tight">
                    Autonomous AI
                    <br />
                    <span className="bg-gradient-to-r from-primary-600 via-secondary-500 to-accent-500 bg-clip-text text-transparent">
                        Content Creation
                    </span>
                </h1>

                <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                    Let AI agents research, write, and optimize your content while you maintain full control
                    with human-in-the-loop checkpoints.
                </p>

                <div className="flex items-center justify-center gap-4">
                    <Link to="/projects/new" className="btn-primary flex items-center gap-2 shadow-lg shadow-primary-500/20">
                        Start Creating
                        <ArrowRight className="w-5 h-5" />
                    </Link>
                    <Link to="/projects" className="btn-secondary flex items-center gap-2 hover:bg-white">
                        <FileText className="w-5 h-5" />
                        View Projects
                    </Link>
                </div>
            </section>

            {/* Features Grid */}
            <section className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {features.map((feature) => (
                    <div key={feature.title} className="card bg-white border-gray-200 hover:border-primary-200 hover:shadow-lg transition-all duration-300">
                        <div className="w-12 h-12 bg-gradient-to-br from-primary-50 to-secondary-50 rounded-xl flex items-center justify-center mb-4">
                            <feature.icon className="w-6 h-6 text-primary-600" />
                        </div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                        <p className="text-gray-600 text-sm">{feature.description}</p>
                    </div>
                ))}
            </section>

            {/* Workflow Section */}
            <section className="space-y-8">
                <div className="text-center">
                    <h2 className="text-3xl font-bold text-gray-900 mb-4">How It Works</h2>
                    <p className="text-gray-600">Five simple steps to publication-ready content</p>
                </div>

                <div className="grid md:grid-cols-5 gap-4">
                    {workflow.map((item, index) => (
                        <div key={item.step} className="relative group">
                            <div className="card text-center bg-white border-gray-200 hover:border-primary-200 hover:shadow-md transition-all duration-300">
                                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mx-auto mb-4 text-white font-bold shadow-md shadow-primary-500/20 group-hover:scale-110 transition-transform">
                                    {item.step}
                                </div>
                                <h3 className="font-semibold text-gray-900 mb-2">{item.title}</h3>
                                <p className="text-gray-500 text-sm">{item.description}</p>
                            </div>

                            {index < workflow.length - 1 && (
                                <div className="hidden md:block absolute top-1/2 -right-2 w-4 text-gray-300">
                                    <ArrowRight className="w-4 h-4" />
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </section>

            {/* CTA Section */}
            <section className="glass rounded-3xl p-12 text-center space-y-6 bg-gradient-to-r from-violet-50 to-fuchsia-50 border border-violet-100">
                <div className="w-20 h-20 bg-white rounded-2xl flex items-center justify-center mx-auto shadow-md">
                    <Search className="w-10 h-10 text-primary-600" />
                </div>
                <h2 className="text-3xl font-bold text-gray-900">Ready to Create?</h2>
                <p className="text-gray-600 max-w-xl mx-auto">
                    Start with a topic and let our AI agents handle the research, writing, and optimization.
                </p>
                <Link to="/projects/new" className="btn-primary inline-flex items-center gap-2 shadow-lg shadow-primary-500/20">
                    Create Your First Post
                    <ArrowRight className="w-5 h-5" />
                </Link>
            </section>
        </div>
    )
}
