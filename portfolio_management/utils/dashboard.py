import html
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objs as go
from portfolio_management.utils.helpers import compute_simulation_metrics, convert_time_steps_to_dates
from portfolio_management.utils.ui import panel, ICON_UP, ICON_DOWN

# One accent (desaturated emerald) plus zinc neutrals; series beyond the accent step through greys.
ACCENT = '#1F8A63'
ZINC_900, ZINC_600, ZINC_500, ZINC_400, ZINC_300 = '#18181B', '#52525B', '#71717A', '#A1A1AA', '#D4D4D8'
SERIES = [ACCENT, ZINC_900, ZINC_400, '#7DBBA2', ZINC_600, ZINC_300, '#2F6B55', ZINC_500]
MUTED = ZINC_500
GRID = '#E4E4E7'
CONFIG = {'displayModeBar': False, 'responsive': True}
MONO = 'Geist Mono, monospace'

def _rgba(hex_color, alpha):
    h = hex_color.lstrip('#')
    return f'rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{alpha})'

def _money(v):
    return f"-${abs(v):,.0f}" if v < 0 else f"${v:,.0f}"

# ---------- HTML pieces (DetailHeader / DetailTag / ChartMarker / Legend) ----------

def _tag(text, positive=None):
    icon = '' if positive is None else (ICON_UP if positive else ICON_DOWN)
    cls = 'mc-tag pos' if positive else 'mc-tag'
    return f'<span class="{cls}">{icon}{html.escape(text)}</span>'

def _detail_header(title, subtitle, tags=()):
    st.markdown(
        f'<div class="mc-detail-head"><div><h3>{html.escape(title)}</h3><p>{html.escape(subtitle)}</p></div>'
        f'<div class="mc-tags">{"".join(tags)}</div></div>',
        unsafe_allow_html=True,
    )

def _legend(series):
    """series: (label, color, dashed)"""
    items = ''.join(
        f'<span><i class="{"dash" if dashed else ""}" style="background:{c};border-color:{c}"></i>{html.escape(label)}</span>'
        for label, c, dashed in series
    )
    st.markdown(f'<div class="mc-legend">{items}</div>', unsafe_allow_html=True)

def _metric_head(title, value, description):
    st.markdown(
        f'<div class="mc-metric"><h3>{html.escape(title)}</h3><div class="v">{html.escape(value)}</div>'
        f'<p>{html.escape(description)}</p></div>',
        unsafe_allow_html=True,
    )

# ---------- Plotly base ----------

def _layout(height, **overrides):
    layout = dict(
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Geist, system-ui, sans-serif', color=MUTED, size=12),
        margin=dict(l=0, r=8, t=8, b=0),
        showlegend=False,
        hovermode='x unified',
        hoverlabel=dict(bgcolor='#FFFFFF', bordercolor=GRID, font=dict(family=MONO, color=ZINC_900, size=12)),
        xaxis=dict(showgrid=False, zeroline=False, showline=False, ticks='', automargin=True, tickfont=dict(size=12)),
        yaxis=dict(gridcolor=GRID, griddash='dash', zeroline=False, showline=False, ticks='', automargin=True, tickfont=dict(size=12)),
    )
    layout.update(overrides)
    return layout

def _sparkline_layout(height=76):
    return _layout(height, margin=dict(l=0, r=0, t=4, b=0), xaxis=dict(visible=False), yaxis=dict(visible=False))

def _gradient_area(x, y, color, baseline, width=2, name=None, hover=None, top_alpha=0.28):
    """Area with a vertical fade (the reference's linearGradient fill), filled down to `baseline`."""
    return [
        go.Scatter(x=x, y=np.full(len(y), baseline), mode='lines', line=dict(width=0), hoverinfo='skip'),
        go.Scatter(
            x=x, y=y, mode='lines', name=name, line=dict(color=color, width=width, shape='spline', smoothing=0.6),
            fill='tonexty',
            fillgradient=dict(type='vertical', colorscale=[[0, _rgba(color, 0)], [1, _rgba(color, top_alpha)]]),
            hovertemplate=hover,
        ),
    ]

def _show(fig):
    # A column is measured from the DOM, so the chart gets the panel's real inner width
    # (a bordered container's width ignores our custom panel padding).
    with st.columns(1)[0]:
        st.plotly_chart(fig, use_container_width=True, theme=None, config=CONFIG)

def _sample_index(n, points=60):
    # ~60 points keeps splines smooth without hiding the shape
    idx = np.arange(0, n, max(1, n // points))
    return idx if idx[-1] == n - 1 else np.append(idx, n - 1)

# ---------- Sections ----------

def _metric_strip(paths, finals, initial_investment, x, m):
    """Metrics separated by hairlines (not boxed), on an asymmetric 5 / 4 / 3 grid."""
    idx = _sample_index(paths.shape[0])
    x = [x[i] for i in idx]
    cols = st.columns([5, 4, 3], gap='medium')

    with cols[0]:
        _metric_head('Expected final value', _money(m['mean']),
                     f"Median {_money(m['median'])}, typical spread {_money(m['std_dev'])}")
        mean_path = paths[idx].mean(axis=1)
        fig = go.Figure(_gradient_area(x, mean_path, ACCENT, float(mean_path.min()) * 0.995,
                                       hover='%{x}<br>$%{y:,.0f}<extra></extra>'))
        fig.update_layout(**_sparkline_layout())
        _show(fig)

    with cols[1]:
        _metric_head('Probability of loss', f"{m['prob_loss']:.1f}%",
                     f"of paths end below {_money(initial_investment)}")
        counts, edges = np.histogram(finals, bins=26)
        centers = (edges[:-1] + edges[1:]) / 2
        colors = [ZINC_900 if c < initial_investment else _rgba(ACCENT, 0.75) for c in centers]
        fig = go.Figure(go.Bar(x=centers, y=counts, marker=dict(color=colors, cornerradius=3),
                               hovertemplate='about $%{x:,.0f}<br>%{y} paths<extra></extra>'))
        fig.update_layout(**_sparkline_layout(), bargap=0.2)
        fig.update_layout(hovermode='closest')
        _show(fig)

    with cols[2]:
        _metric_head('Value at Risk, 95%', _money(m['var_95']),
                     f"Worst-5% average loss {_money(m['cvar_95'])}")
        var_path = initial_investment - np.percentile(paths[idx], 5, axis=1)
        fig = go.Figure(_gradient_area(x, var_path, ZINC_600, float(min(var_path.min(), 0)),
                                       hover='%{x}<br>VaR $%{y:,.0f}<extra></extra>', top_alpha=0.2))
        fig.update_layout(**_sparkline_layout())
        _show(fig)

def _sample_paths_trace(x, paths, n=60):
    """Individual simulations as one faint trace (None gaps separate paths; one trace keeps rendering fast)."""
    cols = np.linspace(0, paths.shape[1] - 1, min(n, paths.shape[1])).astype(int)
    xs, ys = [], []
    for c in cols:
        xs.extend(x + [None])
        ys.extend(list(paths[:, c]) + [None])
    return go.Scatter(x=xs, y=ys, mode='lines', line=dict(color='rgba(161,161,170,0.28)', width=1),
                      hoverinfo='skip', connectgaps=False), paths[:, cols]

def _performance_card(paths, finals, initial_investment, start_date, num_simulations, m):
    idx = _sample_index(paths.shape[0], points=90)  # enough points to keep each path's day-to-day texture
    x = convert_time_steps_to_dates(start_date, idx)
    sampled = paths[idx]
    p5, p50, p95 = np.percentile(sampled, [5, 50, 95], axis=1)
    change = (m['mean'] - initial_investment) / initial_investment * 100 if initial_investment else 0.0

    with st.container(border=True):
        panel()
        _detail_header(
            'Portfolio trajectory',
            f'60 of {num_simulations:,} simulated paths, with the median and the 5th and 95th percentile',
            [_tag(f"{change:+.1f}% expected", positive=change >= 0), _tag(f"Sharpe {m['sharpe']:.2f}")],
        )
        fig = go.Figure()
        paths_trace, shown = _sample_paths_trace(x, sampled)
        fig.add_trace(paths_trace)
        lo = float(min(shown.min(), p5.min(), initial_investment)) * 0.98
        hi = float(max(shown.max(), p95.max())) * 1.02
        fig.add_hline(y=initial_investment, line=dict(color=ZINC_300, width=1, dash='3px,5px'))
        fig.add_trace(go.Scatter(x=x, y=p95, mode='lines', name='95th percentile',
                                 line=dict(color=ZINC_500, width=1.75, dash='7px,5px'),
                                 hovertemplate='95th  $%{y:,.0f}<extra></extra>'))
        fig.add_trace(go.Scatter(x=x, y=p5, mode='lines', name='5th percentile',
                                 line=dict(color=ZINC_400, width=1.75, dash='2px,5px'),
                                 hovertemplate='5th  $%{y:,.0f}<extra></extra>'))
        fig.add_trace(go.Scatter(x=x, y=p50, mode='lines', name='Median', line=dict(color=ACCENT, width=2.75),
                                 hovertemplate='Median  $%{y:,.0f}<extra></extra>'))
        fig.add_trace(go.Scatter(x=[x[-1]], y=[p50[-1]], mode='markers', hoverinfo='skip',
                                 marker=dict(color=ACCENT, size=9, line=dict(color='#FFFFFF', width=2))))
        fig.update_layout(**_layout(
            384,
            xaxis=dict(showgrid=False, zeroline=False, showline=False, ticks='', automargin=True, nticks=5, tickformat='%b %Y', tickfont=dict(size=12)),
            yaxis=dict(range=[lo, hi], automargin=True, showgrid=False, zeroline=False, showline=False, ticks='',
                       tickprefix='$', tickformat='~s', tickfont=dict(family=MONO, size=11)),
        ))
        _show(fig)
        _legend([('Median', ACCENT, False), ('Individual simulations', 'rgba(161,161,170,0.55)', False),
                 ('95th percentile', ZINC_500, True), ('5th percentile', ZINC_400, True),
                 (f'Invested {_money(initial_investment)}', ZINC_300, True)])
        st.markdown('<div class="mc-rule"></div>', unsafe_allow_html=True)
        _metric_strip(paths, finals, initial_investment, convert_time_steps_to_dates(start_date, np.arange(paths.shape[0])), m)

def _annual_returns(stock_data):
    yearly = stock_data.groupby(stock_data.index.year).agg(['first', 'last'])
    returns = pd.DataFrame({t: yearly[(t, 'last')] / yearly[(t, 'first')] - 1 for t in stock_data.columns})
    return returns * 100

def _bar_panel_layout(values, stacked=False):
    lo, hi = float(np.nanmin(values)), float(np.nanmax(values))
    lower = min(0.0, np.floor(lo / 10) * 10)
    upper = max(10.0, np.ceil(hi / 10) * 10)
    return _layout(
        300,
        barmode='relative' if stacked else 'group',
        bargap=0.3, bargroupgap=0.08,
        xaxis=dict(type='category', tickangle=0, automargin=True, showgrid=False, zeroline=False, showline=False, ticks='', tickfont=dict(size=12)),
        yaxis=dict(range=[lower, upper], automargin=True, gridcolor=GRID, griddash='dash', zeroline=True, zerolinecolor=ZINC_300,
                   showline=False, ticks='', ticksuffix='%', tickfont=dict(family=MONO, size=11)),
    )

def _analytics_panels(stock_data, weights, names):
    tickers = list(stock_data.columns)
    name = {tk: names.get(tk, tk) for tk in tickers}  # full company names in results; tickers only for selection
    colors = {t: SERIES[i % len(SERIES)] for i, t in enumerate(tickers)}
    yearly = _annual_returns(stock_data)
    years = [str(y) for y in yearly.index]
    labels = [f"'{y[2:]}" for y in years] if len(years) > 5 else years  # short labels stay legible in narrow cards
    weights = np.asarray(weights, dtype=float)
    contrib = yearly.mul(weights, axis=1)
    portfolio_by_year = contrib.sum(axis=1)
    best = yearly.mean().idxmax()
    partial = f' ({years[-1]} is year to date)' if len(years) > 1 else ''

    cols = st.columns([6, 5], gap='small')

    with cols[0]:
        with st.container(border=True):
            panel(delay=1)
            _detail_header('Annual returns', f'Calendar-year price change of each stock{partial}',
                           [_tag(f'Best average: {name[best]}')])
            _legend([(name[t], colors[t], False) for t in tickers])
            fig = go.Figure([
                go.Bar(x=labels, y=yearly[t], name=name[t], marker=dict(color=colors[t], cornerradius=4),
                       hovertemplate='%{fullData.name}  %{y:.1f}%<extra></extra>')
                for t in tickers
            ])
            fig.update_layout(**_bar_panel_layout(yearly.values))
            _show(fig)

    with cols[1]:
        with st.container(border=True):
            panel(delay=2)
            avg = portfolio_by_year.mean()
            _detail_header('Return contribution', 'Weight times yearly return: what each stock added',
                           [_tag(f"{avg:+.1f}% a year on average", positive=avg >= 0)])
            _legend([(f'{name[t]} {w * 100:.0f}%', colors[t], False) for t, w in zip(tickers, weights)])
            fig = go.Figure([
                go.Bar(x=labels, y=contrib[t], name=name[t], marker=dict(color=colors[t], cornerradius=5),
                       hovertemplate='%{fullData.name}  %{y:.1f}%<extra></extra>')
                for t in tickers
            ])
            pos = contrib.clip(lower=0).sum(axis=1).max()
            neg = contrib.clip(upper=0).sum(axis=1).min()
            fig.update_layout(**_bar_panel_layout(np.array([pos, neg]), stacked=True))
            _show(fig)

def render_dashboard(paths, finals, initial_investment, start_date, num_simulations, stock_data, weights, names=None):
    m = compute_simulation_metrics(finals, initial_investment)
    _performance_card(paths, finals, initial_investment, start_date, num_simulations, m)
    _analytics_panels(stock_data, weights, names or {})
