from collections import Counter
import datetime
from datetime import timedelta
import multiprocessing
import random

from astropy.time import Time
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from poliastro.bodies import Earth
from poliastro.frames import Planes
from poliastro.plotting import OrbitPlotter3D
from poliastro.plotting.static import StaticOrbitPlotter
import plotly.graph_objects as go
from concurrent.futures import ProcessPoolExecutor

from .service import Neo
from .utils import compute_neo_position, create_orbit

class NeoVisualizationError(Exception):
    """Custom exception for NEO visualization errors."""

class Show:
    def __init__(self, neo_service: Neo):
        """Initialize with a Neo service instance."""
        self.neo_service = neo_service

    def _get_random_neos(self, number: int, date: datetime.datetime = None) -> tuple[list, Time]:
        """
        Get random NEOs and epoch for visualization.
        
        :param number: Number of NEOs to select
        :param date: Date for epoch calculation (default: current date)
        :return: Tuple of (selected NEOs list, epoch)
        :raises NeoVisualizationError: If no NEO data is available
        """
        date = date or datetime.datetime.now()
        epoch = Time(date, scale="tdb")  # TDB scale for JPL data
        
        # Fetch all NEOs
        neo_objs = self.neo_service.all()
        if not neo_objs:
            raise NeoVisualizationError("No NEO data available.")

        # Randomly select a subset of NEOs
        neo_sample = random.sample(neo_objs, min(number, len(neo_objs)))
        
        return neo_sample, epoch

    def _compute_positions(self, neos: list, epoch: Time) -> list:
        """
        Compute NEO positions using multiprocessing.
        
        :param neos: List of NEOs to process
        :param epoch: Time epoch for position calculation
        :return: List of valid position results
        :raises NeoVisualizationError: If no valid positions computed
        """
        # Compute positions using multiprocessing
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            results = pool.starmap(
                compute_neo_position, 
                [(neo, epoch) for neo in neos]
            )

        # Filter out invalid results
        valid_positions = [res for res in results if res is not None]
        
        if not valid_positions:
            raise NeoVisualizationError("No valid NEO positions computed.")
            
        return valid_positions

    def random(self, number: int):
        """
        Plot random Near-Earth Objects (NEOs) at the current date in 2D.
        
        :param number: The number of random NEOs to plot.
        """
        try:
            neo_sample, epoch = self._get_random_neos(number)
            positions = self._compute_positions(neo_sample, epoch)
            
            # Initialize Matplotlib figure
            _, ax = plt.subplots()
            title = f"{number} NEOs on {epoch.datetime.strftime('%Y-%m-%d')}"
            ax.set_title(title)
            ax.set_facecolor("black")
            ax.set_xlim(-2e+8, 2e+8)
            ax.set_ylim(-2e+8, 2e+8)
            plotter = StaticOrbitPlotter(ax=ax, plane=Planes.EARTH_ECLIPTIC)

            x_positions, y_positions, _ = zip(*positions)
            ax.scatter(x_positions, y_positions, s=0.8, c="white", marker=".")

            # Plot Earth's orbit
            earth_traj, earth_pos = plotter.plot_body_orbit(
                Earth, epoch, label="Earth", color="blue"
            )
            earth_traj[0].set_linewidth(0.5)
            earth_pos.set_markersize(5)

            plt.show()
        except (NeoVisualizationError, ValueError, TypeError, RuntimeError) as e:
            print(f"Error in random(): {e}")

    def random3d(self, number: int):
        """
        Plot Earth's orbit using OrbitPlotter3D and NEOs using Plotly in 3D.
        
        :param number: The number of random NEOs to plot.
        """
        try:
            neo_sample, epoch = self._get_random_neos(number)
            neo_positions = self._compute_positions(neo_sample, epoch)

            x_neo, y_neo, z_neo = zip(*neo_positions)

            # Create a Plotly figure
            fig = go.Figure()
            frame = OrbitPlotter3D(
                figure=fig, 
                plane=Planes.EARTH_ECLIPTIC, 
                dark=True
            )

            # Plot Earth's orbit
            frame.plot_body_orbit(Earth, epoch, label="Earth", color="blue")

            # Plot NEOs as red dots
            fig.add_trace(go.Scatter3d(
                x=x_neo, 
                y=y_neo, 
                z=z_neo,
                mode='markers',
                marker=dict(size=2, color='red'),
                name='NEOs'
            ))

            # Save and open the interactive plot
            fig.write_html("neo_3d_output.html", auto_open=True)
        except (NeoVisualizationError, ValueError, TypeError, RuntimeError) as e:
            print(f"Error in random3d(): {e}")
        
    def possible_impacts(
        self, 
        from_date: datetime, 
        to_date: datetime, 
        show_labels: bool = False
    ):
        """
        Generate a bubble chart where:
        - X-axis: Impact date
        - Y-axis: Probability of impact
        - Bubble size: NEO diameter
        - Bubble color: Unique per NEO
        
        :param from_date: The start date for filtering NEOs.
        :param to_date: The end date for filtering NEOs.
        :param show_labels: Whether to show labels for each bubble with NEO name 
                           and diameter.
        """
        neos = self.neo_service.by_potential_impact_dates(from_date, to_date)
        
        if not neos:
            print("No NEOs found in the given date range.")
            return

        dates = []
        probabilities = []
        sizes = []
        labels = []
        colors = {}
        legend_labels = {}
        
        for neo in neos:
            for impact in neo.possible_impacts:
                if from_date <= impact.datetime_utc <= to_date:
                    dates.append(impact.datetime_utc)
                    probabilities.append(impact.probability)
                    sizes.append(neo.diameter * 2)  # Scale bubble size
                    if show_labels:
                        labels.append(f"{neo.name} ({neo.diameter}m)")
                    random_color = (
                        random.random(), 
                        random.random(), 
                        random.random()
                    )
                    colors[neo.name] = random_color
                    legend_labels[neo.name] = (
                        f"{neo.name}: {impact.probability:.10f}% | "
                        f"{neo.diameter} m | {impact.expected_energy_in_mt} MT | "
                        f"{impact.datetime_utc.strftime('%Y-%m-%d')}"
                    )
                    break
        
        scatter_colors = [
            colors[neo.name] 
            for neo in neos
        ]
        plt.figure(figsize=(12, 6))
        plt.scatter(
            dates, probabilities, s=sizes, c=scatter_colors, 
            alpha=0.6, edgecolors='w'
        )
        
        for i, label in enumerate(labels):
            plt.annotate(
                label, 
                (dates[i], probabilities[i]), 
                fontsize=7, 
                ha='right', 
                color='blue'
            )
        
        plt.xlabel("Impact Date")
        plt.ylabel("Impact Probability")
        plt.title("NEO Bubble Chart: Impact Probability, Date & Size")
        plt.xticks(rotation=45)
        plt.subplots_adjust(right=0.65, bottom=0.2)
        plt.xlim(from_date - timedelta(days=1), to_date + timedelta(days=1))
        
        # Create legend handles
        legend_handles = [
            Line2D(
                [0], [0], 
                marker='o', 
                color=color, 
                markerfacecolor=color, 
                markersize=7, 
                label=label
            ) for label, color in zip(legend_labels.values(), colors.values())
        ]
        
        # Add legend with custom title and position
        plt.legend(
            handles=legend_handles, 
            title='Probability | Size | Impact Energy | Impact Date', 
            loc='upper left', 
            bbox_to_anchor=(1, 1), 
            fontsize=7, 
            frameon=True
        )
        
        plt.grid()
        plt.show()
        
    def orbit_2D(
        self,
        neo_name: str, 
        date: datetime = datetime.datetime.now(), 
        fixed_view_limits: bool = False
    ):
        """
        Show the 2D orbit of a Near-Earth Object (NEO) using Poliastro.
        
        :param neo_name: The name of the NEO.
        :param date: The date at which to show the orbit.
        :param fixed_view_limits: Whether to fix the view limits to a predefined 
                                range.
        """
        try:
            neo = self.neo_service.from_name(neo_name)
            if not neo:
                raise NeoVisualizationError(f"NEO '{neo_name}' not found.")
            
            epoch = Time(date, scale="tdb")                
            _, ax = plt.subplots()
            ax.set_title(f"{neo_name} on {date.strftime('%Y-%m-%d')}")
            ax.set_facecolor("black")
            if fixed_view_limits:
                ax.set_xlim(-2e+8, 2e+8)
                ax.set_ylim(-2e+8, 2e+8)
            plotter = StaticOrbitPlotter(
                ax=ax, 
                plane=Planes.EARTH_ECLIPTIC
            )
            neo_orbit = create_orbit(neo, epoch)
            plotter.plot(neo_orbit, label=neo_name, color="red")
            plotter.plot_body_orbit(Earth, epoch, label="Earth", color="blue")
            plt.show()
        except (NeoVisualizationError, ValueError, TypeError, RuntimeError) as e:
            print(f"Error in show_orbit_2D(): {e}")
            
    def orbit_3D(
        self,
        neo_name: str, 
        date: datetime = datetime.datetime.now()
    ):
        """
        Show the 3D orbit of a Near-Earth Object (NEO) using Poliastro.
        
        :param neo_name: The name of the NEO.
        :param date: The date at which to show the orbit.
        """
        try:            
            neo = self.neo_service.from_name(neo_name)
            if not neo:
                raise NeoVisualizationError(f"NEO '{neo_name}' not found.")
            
            epoch = Time(date, scale="tdb")
            neo_orbit = create_orbit(neo, epoch)
            
            # Create a Plotly figure
            fig = go.Figure()
            
            # Plot NEO and Earth orbits
            frame = OrbitPlotter3D(
                figure=fig, 
                plane=Planes.EARTH_ECLIPTIC, 
                dark=True
            )
            frame.plot(neo_orbit, label=neo_name, color="red")
            frame.plot_body_orbit(Earth, epoch, label="Earth", color="blue")
            
            # Save and open the interactive plot
            fig.write_html("neo_3d_output.html", auto_open=True)
        except (NeoVisualizationError, ValueError, TypeError, RuntimeError) as e:
            print(f"Error in show_orbit_3D(): {e}")
            
    def orbital_groups(self):
        """
        Plot a bar chart showing the distribution of orbit types among Near-Earth 
        Objects.
        """
        neo_objs = self.neo_service.all()
        
        if not neo_objs:
            print("No NEO data available.")
            return
        
        # Extract orbit types
        orbit_types = [
            neo.orbit_properties.orbit_type 
            for neo in neo_objs 
            if neo.orbit_properties and neo.orbit_properties.orbit_type
        ]
        
        # Count occurrences of each orbit type
        orbit_counts = Counter(orbit_types)
        
        # Plot bar chart
        plt.figure(figsize=(10, 6))
        plt.bar(orbit_counts.keys(), orbit_counts.values(), color='skyblue')
        
        plt.xlabel("Orbit Type")
        plt.ylabel("Count")
        plt.title("Distribution of NEO Orbit Types")
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.show()