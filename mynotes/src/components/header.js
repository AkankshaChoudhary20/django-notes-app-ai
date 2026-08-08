import { Link } from "react-router-dom";

const Header = () => {
    return (
        <div className="app-header">
            <Link to="/"><h1>My Notes</h1></Link>
            <Link to="/ask" className="ask-nav-link">Ask</Link>
        </div>
    )
}

export default Header