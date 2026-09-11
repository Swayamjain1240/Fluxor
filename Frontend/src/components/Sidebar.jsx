import {
    NavLink
} from "react-router-dom";


const Sidebar = () => {

    const getLinkStyle = ({
        isActive
    }) => {

        return {

            display: "flex",

            alignItems: "center",

            gap: "12px",

            padding: "12px 14px",

            textDecoration: "none",

            borderRadius: "8px",

            color:
                isActive
                    ? "#ffffff"
                    : "#9ba3b2",

            background:
                isActive
                    ? "#202633"
                    : "transparent",

            border:
                isActive
                    ? "1px solid #303848"
                    : "1px solid transparent",

            fontSize: "14px",

            fontWeight:
                isActive
                    ? "600"
                    : "500"
        };
    };


    const links = [

        {
            path: "/dashboard",
            icon: "◫",
            label: "Dashboard"
        },

        {
            path: "/datasets",
            icon: "◩",
            label: "Datasets"
        },

        {
            path: "/candidates",
            icon: "◉",
            label: "Candidates"
        },

        {
            path: "/investigations",
            icon: "◇",
            label: "Investigations"
        },

        {
            path: "/validations",
            icon: "✓",
            label: "Validations"
        }

    ];


    return (

        <aside
            style={{
                width: "240px",

                minHeight: "100vh",

                height: "100vh",

                padding: "24px 18px",

                background: "#0d1017",

                borderRight:
                    "1px solid #242936",

                position: "fixed",

                left: 0,

                top: 0,

                display: "flex",

                flexDirection: "column",

                boxSizing: "border-box",

                zIndex: 100
            }}
        >

            <div
                style={{
                    padding: "4px 6px 22px"
                }}
            >

                <h2
                    style={{
                        margin: 0,
                        color: "#ffffff",
                        letterSpacing: "3px"
                    }}
                >

                    FLUXOR

                </h2>


                <span
                    style={{
                        display: "block",
                        marginTop: "6px",
                        color: "#818898",
                        fontSize: "11px"
                    }}
                >

                    Scientific Intelligence

                </span>

            </div>


            <nav
                style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "7px",
                    marginTop: "10px"
                }}
            >

                <p
                    style={{
                        margin: "0 0 8px 8px",
                        color: "#626b7a",
                        fontSize: "10px",
                        fontWeight: "700",
                        letterSpacing: "1.2px"
                    }}
                >

                    RESEARCH

                </p>


                {
                    links.map(
                        (
                            link
                        ) => (

                            <NavLink
                                key={
                                    link.path
                                }

                                to={
                                    link.path
                                }

                                style={
                                    getLinkStyle
                                }
                            >

                                <span
                                    style={{
                                        width: "22px",
                                        textAlign: "center"
                                    }}
                                >

                                    {
                                        link.icon
                                    }

                                </span>


                                {
                                    link.label
                                }

                            </NavLink>

                        )
                    )
                }

            </nav>


            <div
                style={{
                    marginTop: "auto",
                    padding: "18px 10px 5px",
                    borderTop: "1px solid #222833"
                }}
            >

                <p
                    style={{
                        margin: 0,
                        color: "#626b7a",
                        fontSize: "11px",
                        lineHeight: "1.6"
                    }}
                >

                    Agentic AI for astronomical
                    transient investigation.

                </p>

            </div>

        </aside>
    );
};


export default Sidebar;