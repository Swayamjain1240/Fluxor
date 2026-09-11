import {
    NavLink
} from "react-router-dom";


const Sidebar = () => {

    const getLinkStyle = ({
        isActive
    }) => {

        return {

            padding:
                "12px 14px",

            textDecoration:
                "none",

            borderRadius:
                "8px",

            color:
                isActive
                    ? "#ffffff"
                    : "#9ba3b2",

            background:
                isActive
                    ? "#202633"
                    : "transparent"
        };
    };


    return (

        <aside
            style={{
                width: "240px",

                minHeight:
                    "100vh",

                padding:
                    "24px 18px",

                background:
                    "#0d1017",

                borderRight:
                    "1px solid #242936",

                position:
                    "fixed",

                left: 0,

                top: 0
            }}
        >

            <div>

                <h2
                    style={{
                        margin: 0,

                        letterSpacing:
                            "3px"
                    }}
                >

                    FLUXOR

                </h2>


                <span
                    style={{
                        display: "block",

                        marginTop: "6px",

                        color: "#818898",

                        fontSize: "12px"
                    }}
                >

                    Scientific Intelligence

                </span>

            </div>


            <nav
                style={{
                    display: "flex",

                    flexDirection:
                        "column",

                    gap: "8px",

                    marginTop:
                        "40px"
                }}
            >

                <NavLink
                    to="/dashboard"
                    style={
                        getLinkStyle
                    }
                >

                    Dashboard

                </NavLink>


                <NavLink
                    to="/datasets"
                    style={
                        getLinkStyle
                    }
                >

                    Datasets

                </NavLink>


                <NavLink
                    to="/candidates"
                    style={
                        getLinkStyle
                    }
                >

                    Candidates

                </NavLink>

            </nav>

        </aside>
    );
};


export default Sidebar;