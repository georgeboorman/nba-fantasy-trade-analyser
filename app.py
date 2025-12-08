import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="NBA Fantasy Team Builder",
    page_icon="🏀",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    import os
    csv_path = 'nba_player_averages_2026.csv'
    
    if not os.path.exists(csv_path):
        st.error(f"Data file not found: {csv_path}. Please run refresh_data.py to generate the data file.")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(csv_path)
        
        if len(df) == 0:
            st.warning("Data file is empty. Please run refresh_data.py to update the data.")
            return pd.DataFrame()
        
        # Ensure Season column exists
        if 'Season' not in df.columns:
            df['Season'] = 2026
        
        # Remove Rk column if it exists
        if 'Rk' in df.columns:
            df = df.drop(columns=['Rk'])
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

df = load_data()

# Use the combined data
df_current = df.copy()

# Get unique player list
players = sorted(df_current['Player'].unique().tolist())

# Stats to display
stat_columns = {
    'PTS': 'Points',
    'AST': 'Assists',
    'TRB': 'Rebounds',
    'STL': 'Steals',
    'BLK': 'Blocks',
    '3P': '3 Pointers',
    'FT%': 'Free Throw %',
    'FG%': 'Field Goal %',
    'TOV': 'Turnovers'
}

# Categories that count for double-doubles and triple-doubles
dd_categories = ['PTS', 'TRB', 'AST', 'STL', 'BLK']

def check_double_triple_double(player_data):
    """
    Check if a player averages a double-double or triple-double.
    Returns: (is_double_double, is_triple_double, categories_count)
    """
    if player_data is None or len(player_data) == 0:
        return False, False, 0
    
    # Count how many categories the player averages >= 10 in
    categories_at_10 = 0
    qualifying_categories = []
    
    for cat in dd_categories:
        if cat in player_data.columns:
            avg_value = player_data[cat].iloc[0] if len(player_data) == 1 else player_data[cat].mean()
            if avg_value >= 10:
                categories_at_10 += 1
                qualifying_categories.append(cat)
    
    is_double_double = categories_at_10 >= 2
    is_triple_double = categories_at_10 >= 3
    
    return is_double_double, is_triple_double, categories_at_10

def get_player_dd_td_info(players_list, df_data):
    """
    Get double-double and triple-double information for a list of players.
    Returns: dict with counts and player details
    """
    if not players_list:
        return {
            'double_double_count': 0,
            'triple_double_count': 0,
            'players_with_dd': [],
            'players_with_td': []
        }
    
    player_data = df_data[df_data['Player'].isin(players_list)].copy()
    
    dd_count = 0
    td_count = 0
    players_with_dd = []
    players_with_td = []
    
    for player in players_list:
        player_row = player_data[player_data['Player'] == player]
        if len(player_row) > 0:
            is_dd, is_td, cat_count = check_double_triple_double(player_row)
            if is_dd:
                dd_count += 1
                players_with_dd.append({
                    'player': player,
                    'categories': cat_count,
                    'is_triple': is_td
                })
            if is_td:
                td_count += 1
                players_with_td.append(player)
    
    return {
        'double_double_count': dd_count,
        'triple_double_count': td_count,
        'players_with_dd': players_with_dd,
        'players_with_td': players_with_td
    }

def calculate_combined_stats(selected_players, df_data):
    """Calculate combined stats for selected players"""
    if not selected_players:
        return None
    
    # Filter data for selected players
    player_data = df_data[df_data['Player'].isin(selected_players)].copy()
    
    if len(player_data) == 0:
        return None
    
    # For percentages, we need to calculate weighted averages
    # For counting stats, we sum them
    stats = {}
    
    # Sum counting stats
    counting_stats = ['PTS', 'AST', 'TRB', 'STL', 'BLK', '3P', 'TOV']
    for stat in counting_stats:
        if stat in player_data.columns:
            stats[stat] = player_data[stat].sum()
    
    # Calculate weighted averages for percentages
    # FT%: weighted by FTA
    # Note: Column name might be 'FT%' (with % sign)
    ft_col = 'FT%' if 'FT%' in player_data.columns else None
    fta_col = 'FTA' if 'FTA' in player_data.columns else None
    ft_made_col = 'FT' if 'FT' in player_data.columns else None
    
    if fta_col and ft_made_col:
        total_ft = player_data[ft_made_col].sum()
        total_fta = player_data[fta_col].sum()
        stats['FT%'] = (total_ft / total_fta * 100) if total_fta > 0 else 0
    elif ft_col and fta_col:
        # If we have FT% directly, use weighted average by FTA
        total_fta = player_data[fta_col].sum()
        if total_fta > 0:
            # Convert percentage to decimal for calculation
            ft_pct_values = player_data[ft_col].values / 100 if player_data[ft_col].max() > 1 else player_data[ft_col].values
            stats['FT%'] = (ft_pct_values * player_data[fta_col].values).sum() / total_fta * 100
        else:
            stats['FT%'] = 0
    elif ft_col:
        # Fallback to simple average
        ft_pct = player_data[ft_col].mean()
        stats['FT%'] = ft_pct * 100 if ft_pct < 1 else ft_pct
    
    # FG%: weighted by FGA
    fg_col = 'FG%' if 'FG%' in player_data.columns else None
    fga_col = 'FGA' if 'FGA' in player_data.columns else None
    fg_made_col = 'FG' if 'FG' in player_data.columns else None
    
    if fga_col and fg_made_col:
        total_fg = player_data[fg_made_col].sum()
        total_fga = player_data[fga_col].sum()
        stats['FG%'] = (total_fg / total_fga * 100) if total_fga > 0 else 0
    elif fg_col and fga_col:
        # If we have FG% directly, use weighted average by FGA
        total_fga = player_data[fga_col].sum()
        if total_fga > 0:
            # Convert percentage to decimal for calculation
            fg_pct_values = player_data[fg_col].values / 100 if player_data[fg_col].max() > 1 else player_data[fg_col].values
            stats['FG%'] = (fg_pct_values * player_data[fga_col].values).sum() / total_fga * 100
        else:
            stats['FG%'] = 0
    elif fg_col:
        # Fallback to simple average
        fg_pct = player_data[fg_col].mean()
        stats['FG%'] = fg_pct * 100 if fg_pct < 1 else fg_pct
    
    return stats

def display_stats(stats, label="Combined Stats", dd_td_info=None):
    """Display stats in a nice format"""
    if stats is None:
        st.info("No players selected")
        return
    
    # Create columns for better layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Points", f"{stats.get('PTS', 0):.1f}")
        st.metric("Assists", f"{stats.get('AST', 0):.1f}")
        st.metric("Rebounds", f"{stats.get('TRB', 0):.1f}")
    
    with col2:
        st.metric("Steals", f"{stats.get('STL', 0):.1f}")
        st.metric("Blocks", f"{stats.get('BLK', 0):.1f}")
        st.metric("3 Pointers", f"{stats.get('3P', 0):.1f}")
    
    with col3:
        st.metric("Free Throw %", f"{stats.get('FT%', 0):.2f}%")
        st.metric("Field Goal %", f"{stats.get('FG%', 0):.2f}%")
        st.metric("Turnovers", f"{stats.get('TOV', 0):.1f}")
    
    # Display double-double and triple-double information
    if dd_td_info:
        st.markdown("---")
        dd_col1, dd_col2 = st.columns(2)
        with dd_col1:
            st.metric("Players with Double-Doubles", dd_td_info['double_double_count'])
        with dd_col2:
            st.metric("Players with Triple-Doubles", dd_td_info['triple_double_count'])
        
        if dd_td_info['players_with_dd']:
            with st.expander("View Double-Double Players"):
                for player_info in dd_td_info['players_with_dd']:
                    dd_type = "Triple-Double" if player_info['is_triple'] else f"Double-Double ({player_info['categories']} categories)"
                    st.write(f"**{player_info['player']}** - {dd_type}")

# Main app
st.title("🏀 NBA Fantasy Team Builder")

# Add cache clear button in sidebar
with st.sidebar:
    if st.button("🔄 Clear Cache & Reload Data"):
        st.cache_data.clear()
        st.rerun()

# Create tabs for different features
tab1, tab2 = st.tabs(["Team Builder", "Trade Comparison"])

with tab1:
    st.header("Build Your Team")
    st.write("Select up to 13 players to build your fantasy team and see their combined statistics.")
    
    # Multi-select for players
    selected_players = st.multiselect(
        "Select Players (up to 13)",
        players,
        max_selections=13,
        help="Choose up to 13 players for your fantasy team"
    )
    
    if len(selected_players) > 13:
        st.warning("You can only select up to 13 players. Please remove some selections.")
        selected_players = selected_players[:13]
    
    if selected_players:
        st.subheader(f"Selected Players ({len(selected_players)}/13)")
        # Display selected players in a nice format
        player_cols = st.columns(min(4, len(selected_players)))
        for idx, player in enumerate(selected_players):
            with player_cols[idx % 4]:
                st.write(f"• {player}")
        
        # Calculate and display combined stats
        st.subheader("Combined Team Statistics")
        combined_stats = calculate_combined_stats(selected_players, df_current)
        dd_td_info = get_player_dd_td_info(selected_players, df_current)
        display_stats(combined_stats, dd_td_info=dd_td_info)
        
        # Show detailed breakdown
        with st.expander("View Individual Player Stats"):
            # Get available columns
            display_cols = ['Player']
            stat_cols = ['PTS', 'AST', 'TRB', 'STL', 'BLK', 'TOV']
            for col in stat_cols:
                if col in df_current.columns:
                    display_cols.append(col)
            
            # Handle 3P column (might be '3P')
            if '3P' in df_current.columns:
                display_cols.append('3P')
            
            # Handle percentage columns
            if 'FT%' in df_current.columns:
                display_cols.append('FT%')
            if 'FG%' in df_current.columns:
                display_cols.append('FG%')
            
            player_data = df_current[df_current['Player'].isin(selected_players)][display_cols].copy()
            
            # Add double-double and triple-double columns
            dd_td_list = []
            for _, row in player_data.iterrows():
                player_name = row['Player']
                player_row = df_current[df_current['Player'] == player_name]
                is_dd, is_td, cat_count = check_double_triple_double(player_row)
                
                if is_td:
                    dd_td_list.append("Triple-Double")
                elif is_dd:
                    dd_td_list.append(f"Double-Double ({cat_count})")
                else:
                    dd_td_list.append("None")
            
            player_data['DD/TD'] = dd_td_list
            
            # Reorder columns to put DD/TD after Player
            cols = ['Player', 'DD/TD'] + [c for c in player_data.columns if c not in ['Player', 'DD/TD']]
            player_data = player_data[cols]
            
            st.dataframe(player_data, use_container_width=True)
    else:
        st.info("Select players from the dropdown above to build your team.")

with tab2:
    st.header("Trade Comparison")
    st.write("Compare two sets of players to evaluate potential trades. Each set can contain one or more players.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Set 1: Your Players")
        set1_players = st.multiselect(
            "Select players for Set 1",
            players,
            key="set1",
            help="Select one or more players for the first set"
        )
        
        if set1_players:
            st.write("**Selected:**")
            for player in set1_players:
                st.write(f"• {player}")
    
    with col2:
        st.subheader("Set 2: Trade Target Players")
        set2_players = st.multiselect(
            "Select players for Set 2",
            players,
            key="set2",
            help="Select one or more players for the second set"
        )
        
        if set2_players:
            st.write("**Selected:**")
            for player in set2_players:
                st.write(f"• {player}")
    
    # Compare stats if both sets have players
    if set1_players and set2_players:
        st.subheader("Comparison")
        
        # Calculate stats for both sets
        set1_stats = calculate_combined_stats(set1_players, df_current)
        set2_stats = calculate_combined_stats(set2_players, df_current)
        
        if set1_stats and set2_stats:
            # Get DD/TD info for both sets
            set1_dd_td = get_player_dd_td_info(set1_players, df_current)
            set2_dd_td = get_player_dd_td_info(set2_players, df_current)
            
            # Create comparison table
            comparison_data = []
            for stat_key, stat_name in stat_columns.items():
                set1_val = set1_stats.get(stat_key, 0)
                set2_val = set2_stats.get(stat_key, 0)
                diff = set1_val - set2_val
                
                comparison_data.append({
                    'Statistic': stat_name,
                    'Set 1': f"{set1_val:.2f}" if stat_key in ['FT%', 'FG%'] else f"{set1_val:.1f}",
                    'Set 2': f"{set2_val:.2f}" if stat_key in ['FT%', 'FG%'] else f"{set2_val:.1f}",
                    'Difference': f"{diff:+.2f}" if stat_key in ['FT%', 'FG%'] else f"{diff:+.1f}"
                })
            
            # Add DD/TD to comparison
            comparison_data.append({
                'Statistic': 'Double-Doubles (Players)',
                'Set 1': str(set1_dd_td['double_double_count']),
                'Set 2': str(set2_dd_td['double_double_count']),
                'Difference': f"{set1_dd_td['double_double_count'] - set2_dd_td['double_double_count']:+d}"
            })
            comparison_data.append({
                'Statistic': 'Triple-Doubles (Players)',
                'Set 1': str(set1_dd_td['triple_double_count']),
                'Set 2': str(set2_dd_td['triple_double_count']),
                'Difference': f"{set1_dd_td['triple_double_count'] - set2_dd_td['triple_double_count']:+d}"
            })
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
            
            # Visual comparison with metrics
            st.subheader("Side-by-Side Comparison")
            comp_col1, comp_col2, comp_col3 = st.columns(3)
            
            with comp_col1:
                st.markdown("### Set 1 Stats")
                display_stats(set1_stats, dd_td_info=set1_dd_td)
            
            with comp_col2:
                st.markdown("### Set 2 Stats")
                display_stats(set2_stats, dd_td_info=set2_dd_td)
            
            with comp_col3:
                st.markdown("### Difference (Set 1 - Set 2)")
                diff_stats = {}
                for stat_key in stat_columns.keys():
                    if stat_key in set1_stats and stat_key in set2_stats:
                        diff_stats[stat_key] = set1_stats[stat_key] - set2_stats[stat_key]
                
                # Display differences
                diff_col1, diff_col2, diff_col3 = st.columns(3)
                
                with diff_col1:
                    st.metric("Points", f"{diff_stats.get('PTS', 0):.1f}")
                    st.metric("Assists", f"{diff_stats.get('AST', 0):.1f}")
                    st.metric("Rebounds", f"{diff_stats.get('TRB', 0):.1f}")
                
                with diff_col2:
                    st.metric("Steals", f"{diff_stats.get('STL', 0):.1f}")
                    st.metric("Blocks", f"{diff_stats.get('BLK', 0):.1f}")
                    st.metric("3 Pointers", f"{diff_stats.get('3P', 0):.1f}")
                
                with diff_col3:
                    st.metric("Free Throw %", f"{diff_stats.get('FT%', 0):.2f}%")
                    st.metric("Field Goal %", f"{diff_stats.get('FG%', 0):.2f}%")
                    st.metric("Turnovers", f"{diff_stats.get('TOV', 0):.1f}")
                
                st.markdown("---")
                st.metric("Double-Doubles", f"{set1_dd_td['double_double_count'] - set2_dd_td['double_double_count']:+d}")
                st.metric("Triple-Doubles", f"{set1_dd_td['triple_double_count'] - set2_dd_td['triple_double_count']:+d}")
        else:
            st.warning("Could not calculate stats for one or both sets.")
    elif set1_players or set2_players:
        st.info("Please select players for both sets to see the comparison.")
    else:
        st.info("Select players in both sets above to compare them.")

