Equal Area Slope

by Andrew Campbell
andrew.j.campbell@aecom.com

This plug-in estimates the equal area slope of polylines using an underlying topography raster.

Estimating the equal area slope of a catchment or flow path is a necessary step in many hydrological calculations. While not a particularly difficult calculation, it can be time-consuming and hard to document, especially when doing rework. This plug-in aims to streamline the process by providing a method for estimating the equal area slopes of all features in the input vector layer. The algorithm creates a virtual layer with the calculated results in its attribute table.

Mathematically equal area slope (EAS) can be expressed as

EAS = (2 * A) / (L ^ 2) - (z / L)

Where,
A = area under line, which can be estimated by the trapezoidal rule
L = length of line
z = elevation of line at its downstream end

Current limitations
• vector and raster layers must be in the same coordinate reference system;
• vector layer extents must reside within raster layer extents;
• vector layer must be a polyline or polygon layer;
• assumes some thought has been put into digitising the flow paths;
• samples only the first band of raster.

Subsequent revisions will improve the plug-in to better handle aforementioned limitations.

Please email me at andrew.j.campbell@aecom.com with any suggested improvements!
