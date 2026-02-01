import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import HomePage from './pages/HomePage'
import ProjectsPage from './pages/ProjectsPage'
import NewProjectPage from './pages/NewProjectPage'
import TitleSelectionPage from './pages/TitleSelectionPage'
import PlanReviewPage from './pages/PlanReviewPage'
import ExecutionPage from './pages/ExecutionPage'
import DraftReviewPage from './pages/DraftReviewPage'
import ExportPage from './pages/ExportPage'

function App() {
    return (
        <Layout>
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/projects" element={<ProjectsPage />} />
                <Route path="/projects/new" element={<NewProjectPage />} />
                <Route path="/projects/:id/titles" element={<TitleSelectionPage />} />
                <Route path="/projects/:id/plan" element={<PlanReviewPage />} />
                <Route path="/projects/:id/execution" element={<ExecutionPage />} />
                <Route path="/projects/:id/draft" element={<DraftReviewPage />} />
                <Route path="/projects/:id/export" element={<ExportPage />} />
            </Routes>
        </Layout>
    )
}

export default App
