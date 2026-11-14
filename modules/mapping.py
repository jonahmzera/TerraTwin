"""Map figures (Plotly) used by the app pages.

The maps are drawn on plain longitude/latitude axes, using TerraTwin's own ~24,500 screened land
cells as the background. They need no external basemap, so they work offline (for example at a
venue with poor internet).
"""

import plotly.express as px
import plotly.graph_objects as go

GROUP_COLORS = {"team": "#E4572E", "known": "#4C78A8", "discovered": "#2CA58D", "lookalike": "#9D9D9D"}
GROUP_LABELS = {"team": "Team site", "known": "Known analogue (validation)", "discovered": "Discovered candidate",
                "lookalike": "Ice-sheet lookalike (terrain only)"}
GROUP_BADGE = {"team": "orange", "known": "blue", "discovered": "green", "lookalike": "gray"}


def _layout(fig, height):
    fig.update_xaxes(range=[-180, 180], title="Longitude", showgrid=False, zeroline=False, constrain="domain")
    fig.update_yaxes(range=[-86, 86], title="Latitude", showgrid=False, zeroline=False, scaleanchor="x",
                     scaleratio=1)
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.12))
    return fig


def _land(cells, color="rgba(150,150,150,0.35)"):
    return go.Scattergl(x=cells["lon"], y=cells["lat"], mode="markers", hoverinfo="skip", showlegend=False,
                        marker=dict(size=2.5, color=color, line=dict(width=0)))


def sites_map(sites, land_cells=None, height=480):
    df = sites.assign(Group=sites["group"].map(GROUP_LABELS))
    fig = px.scatter(
        df, x="lon", y="lat", color="Group", hover_name="name",
        hover_data={"country": True, "lat": ":.2f", "lon": ":.2f", "Group": False},
        color_discrete_map={GROUP_LABELS[k]: v for k, v in GROUP_COLORS.items()},
    )
    fig.update_traces(marker=dict(size=11, line=dict(width=1, color="white")))
    if land_cells is not None:
        fig.add_trace(_land(land_cells))
        fig.data = (fig.data[-1],) + fig.data[:-1]  # land underneath the sites
    return _layout(fig, height)


def screen_map(cells, highlight=None, height=520):
    """Global stage-1 similarity map: one dot per ~78 km land cell."""
    fig = go.Figure(go.Scattergl(
        x=cells["lon"], y=cells["lat"], mode="markers",
        marker=dict(size=3, color=cells["score"], colorscale="Viridis", cmin=0, cmax=100,
                    colorbar=dict(title="Terrain<br>similarity", len=0.7)),
        customdata=cells[["score"]], hovertemplate="lat %{y:.2f}, lon %{x:.2f}<br>score %{customdata[0]:.0f}<extra></extra>",
        showlegend=False,
    ))
    if highlight is not None and len(highlight):
        fig.add_trace(go.Scatter(x=highlight["lon"], y=highlight["lat"], mode="markers", name="Stage-2 candidates",
                                 marker=dict(size=14, symbol="star", color="#E4572E", line=dict(width=1, color="white")),
                                 text=highlight["label"], hoverinfo="text"))
    return _layout(fig, height)
