from manim import *
import math


class InvoluteGear(Polygon):
    """
    A Manim Micro-library for creating physically accurate involute spur gears.
    Outputs a single, closed, continuous Manim Polygon without self-intersections.
    """
    def __init__(
        self,
        z=15,
        m=0.5,
        alpha_deg=20.0,
        profile_shift=0.0,
        internal=False,
        thickness=2.0,
        undercut_auto_suppress=False,
        num_points=(20, 20, 20, 20),
        tooth_phase=0.0,
        **kwargs
    ):
        self.z = z
        self.m = m
        self.alpha_deg = alpha_deg
        self.profile_shift = profile_shift
        self.internal = internal
        self.thickness = thickness
        self.undercut_auto_suppress = undercut_auto_suppress
        self.num_points = num_points
        # tooth_phase: fraction of a tooth to shift the profile by (0.5 ==> half tooth)
        self.tooth_phase = float(tooth_phase)
        # angle (radians) corresponding to the tooth_phase; useful to call instance.rotate(...)
        self.tooth_phase_angle = float(tooth_phase) * 2.0 * math.pi / float(self.z)

        # 1. Generate the raw mathematical segments
        if self.internal:
            profile = self._generate_internal_tooth_profile()
        else:
            profile = self._generate_external_tooth_profile()

        self.params = profile['parameters']

        # 2. Pattern the single tooth radially matching exact sequence direction
        full_gear_points_3d = self._build_full_gear_points(profile)

        # 3. Initialize the Manim Polygon with the continuous point sequence
        super().__init__(*full_gear_points_3d, **kwargs)

        self.rotate(self.tooth_phase_angle)

    # ---------------------------------------------------------
    # MANIM POLYGON SEQUENCING
    # ---------------------------------------------------------

    def _append_clean(self, target_list, segment_points):
        """Appends points while skipping duplicates to prevent zero-length Manim vectors."""
        for p in segment_points:
            if not target_list:
                target_list.append(p)
            else:
                last_p = target_list[-1]
                # Only add point if distinctly separated from the last point
                if math.hypot(p[0] - last_p[0], p[1] - last_p[1]) > 1e-6:
                    target_list.append(p)

    def _build_external_tooth_sequence(self, p):
        """Strictly traces the perimeter of an external tooth from right-gap to left-gap."""
        pts =[]
        if p.get('trochoid_1'): self._append_clean(pts, reversed(p['trochoid_1']))
        if p.get('involute_1'): self._append_clean(pts, p['involute_1'])
        if p.get('upper_arc'):  self._append_clean(pts, p['upper_arc'])
        if p.get('involute_2'): self._append_clean(pts, reversed(p['involute_2']))
        if p.get('trochoid_2'): self._append_clean(pts, p['trochoid_2'])
        if p.get('lower_arc'):  self._append_clean(pts, p['lower_arc'])
        return pts

    def _build_internal_inner_sequence(self, p):
        """Strictly traces the INNER perimeter of an internal tooth slice."""
        pts =[]
        if p.get('lower_arc_2'): self._append_clean(pts, reversed(p['lower_arc_2']))
        if p.get('involute_1'):  self._append_clean(pts, p['involute_1'])
        if p.get('upper_arc'):   self._append_clean(pts, p['upper_arc'])
        if p.get('involute_2'):  self._append_clean(pts, reversed(p['involute_2']))
        if p.get('lower_arc_1'): self._append_clean(pts, p['lower_arc_1'])
        return pts

    def _build_full_gear_points(self, profile):
        """Patterns the single tooth around 360 degrees."""
        full_pts =[]
        angle_step = 2 * math.pi / self.z

        if not self.internal:
            # EXTERNAL GEAR: Standard continuous outer perimeter.
            tooth_pts = self._build_external_tooth_sequence(profile)
            for i in range(self.z):
                # We MUST tile with negative angle to match the clockwise drawing order of the tooth
                theta = -i * angle_step
                for x, y in tooth_pts:
                    rot_x = x * math.cos(theta) - y * math.sin(theta)
                    rot_y = x * math.sin(theta) + y * math.cos(theta)
                    full_pts.append([rot_x, rot_y, 0.0])
        else:
            # INTERNAL GEAR: Create a hollow ring shape.
            inner_pts = self._build_internal_inner_sequence(profile)
            outer_pts = profile['external_arc']
            
            # Step 1: Trace entire 360° INNER profile (clockwise)
            for i in range(self.z):
                theta = -i * angle_step
                for x, y in inner_pts:
                    rot_x = x * math.cos(theta) - y * math.sin(theta)
                    rot_y = x * math.sin(theta) + y * math.cos(theta)
                    full_pts.append([rot_x, rot_y, 0.0])

            # Step 2: Trace entire 360° OUTER profile BACKWARDS (counter-clockwise)
            # This guarantees Manim draws a single connecting seam, then loops around the back
            for i in reversed(range(self.z)):
                theta = -i * angle_step
                for x, y in reversed(outer_pts):
                    rot_x = x * math.cos(theta) - y * math.sin(theta)
                    rot_y = x * math.sin(theta) + y * math.cos(theta)
                    full_pts.append([rot_x, rot_y, 0.0])

        return full_pts

    # ---------------------------------------------------------
    # GEAR MATHEMATICS GENERATORS
    # ---------------------------------------------------------

    @staticmethod
    def _involute_func(angle):
        return math.tan(angle) - angle

    @staticmethod
    def _rotate_points(points, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return[(x * cos_a - y * sin_a, x * sin_a + y * cos_a) for x, y in points]

    def _generate_external_tooth_profile(self):
        z, m = self.z, self.m
        alpha = math.radians(self.alpha_deg)
        pitch_radius = m * z / 2.0
        base_radius = pitch_radius * math.cos(alpha)
        
        if self.undercut_auto_suppress and base_radius > pitch_radius - m:
            self.profile_shift = base_radius - (pitch_radius - m)
            
        pitch_radius += self.profile_shift
        addendum_radius = pitch_radius + m
        dedendum_radius = max(pitch_radius - 1.25 * m, 0.01)
        
        if base_radius > pitch_radius:
            raise ValueError("Base radius is larger than pitch radius.")
            
        phi = self._involute_func(math.acos(base_radius / pitch_radius))
        angular_tooth_width = math.pi / z
        
        addendum_inv_angle = math.acos(base_radius / addendum_radius)
        max_inv_angle = addendum_inv_angle + self._involute_func(addendum_inv_angle)
        
        dedendum_inv_angle = math.acos(base_radius / dedendum_radius) if base_radius < dedendum_radius else 0
        min_inv_angle = dedendum_inv_angle + self._involute_func(dedendum_inv_angle)
        
        tooth_angle = -angular_tooth_width - 2 * phi
        
        involute_1, involute_2 = [],[]
        n_inv = max(2, self.num_points[0])
        for i in range(n_inv):
            t = float(i) / (n_inv - 1)
            theta = t * (max_inv_angle - min_inv_angle) + min_inv_angle
            x_inv = base_radius * (math.cos(theta) + theta * math.sin(theta))
            y_inv = base_radius * (math.sin(theta) - theta * math.cos(theta))
            
            c_t, s_t = math.cos(tooth_angle), math.sin(tooth_angle)
            involute_2.append((x_inv * c_t - y_inv * s_t, x_inv * s_t + y_inv * c_t))
            involute_1.append((x_inv, -y_inv))
            
        trochoid_1, trochoid_2 = [], []
        n_tro = max(2, self.num_points[1])
        if base_radius > dedendum_radius:
            t_trochoid = base_radius - dedendum_radius
            b_trochoid = math.sqrt(base_radius**4 / (base_radius - t_trochoid)**2 - base_radius**2)
            h_trochoid = b_trochoid * (1 - t_trochoid / base_radius)
            
            alpha_trochoid = math.atan(h_trochoid / base_radius)
            offset_trochoid_angle = alpha_trochoid + self._involute_func(alpha_trochoid)
            beta_trochoid = math.atan(b_trochoid / base_radius) - offset_trochoid_angle

            for i in range(n_tro):
                t = float(i) / (n_tro - 1)
                theta_tro = t * offset_trochoid_angle
                x_tro = base_radius * (math.cos(theta_tro) + theta_tro * math.sin(theta_tro)) - t_trochoid * math.cos(theta_tro)
                y_tro = base_radius * (math.sin(theta_tro) - theta_tro * math.cos(theta_tro)) - t_trochoid * math.sin(theta_tro)
                
                c_b, s_b = math.cos(beta_trochoid), math.sin(beta_trochoid)
                x_tro_r = x_tro * c_b - y_tro * s_b
                y_tro_r = x_tro * s_b + y_tro * c_b
                
                trochoid_1.append((x_tro_r, y_tro_r))
                c_t, s_t = math.cos(tooth_angle), math.sin(tooth_angle)
                trochoid_2.append((x_tro_r * c_t - (-y_tro_r) * s_t, x_tro_r * s_t + (-y_tro_r) * c_t))
                
            trochoid_1.reverse()
            trochoid_2.reverse()

        upper_arc =[]
        n_up = max(2, self.num_points[2])
        inv_at_add = self._involute_func(math.acos(base_radius / addendum_radius))
        start_u, end_u = -inv_at_add, tooth_angle + inv_at_add
        for i in range(n_up):
            t = float(i) / (n_up - 1)
            theta_arc = start_u + t * (end_u - start_u)
            upper_arc.append((addendum_radius * math.cos(theta_arc), addendum_radius * math.sin(theta_arc)))
            
        lower_arc =[]
        n_low = max(2, self.num_points[3])
        if base_radius > dedendum_radius:
            start_l, end_l = tooth_angle - beta_trochoid, -angular_tooth_width * 2 + beta_trochoid
        else:
            start_l = tooth_angle + self._involute_func(dedendum_inv_angle)
            end_l = -angular_tooth_width * 2 - self._involute_func(dedendum_inv_angle)
            
        for i in range(n_low):
            t = float(i) / (n_low - 1)
            theta_arc = start_l + t * (end_l - start_l)
            lower_arc.append((dedendum_radius * math.cos(theta_arc), dedendum_radius * math.sin(theta_arc)))

        rotation_angle = -tooth_angle / 2
        return {
            'trochoid_1': self._rotate_points(trochoid_1, rotation_angle),
            'involute_1': self._rotate_points(involute_1, rotation_angle),
            'upper_arc':  self._rotate_points(upper_arc, rotation_angle),
            'involute_2': self._rotate_points(involute_2, rotation_angle),
            'trochoid_2': self._rotate_points(trochoid_2, rotation_angle),
            'lower_arc':  self._rotate_points(lower_arc, rotation_angle),
            'parameters': {'pitch_radius': pitch_radius}
        }

    def _generate_internal_tooth_profile(self):
        z, m = self.z, self.m
        alpha = math.radians(self.alpha_deg)
        pitch_radius = m * z / 2.0
        base_radius = pitch_radius * math.cos(alpha)
        
        if self.undercut_auto_suppress and base_radius > pitch_radius - m:
            self.profile_shift = base_radius - (pitch_radius - m)
            
        pitch_radius += self.profile_shift
        addendum_radius = pitch_radius - m
        dedendum_radius = max(pitch_radius + 1.25 * m, 0.01)
        
        phi = self._involute_func(math.acos(base_radius / pitch_radius))
        angular_tooth_width = math.pi / z
        
        dedendum_inv_angle = math.acos(base_radius / dedendum_radius)
        addendum_inv_angle = math.acos(base_radius / addendum_radius) if base_radius < addendum_radius else 0
        
        max_inv_angle = dedendum_inv_angle + self._involute_func(dedendum_inv_angle)
        min_inv_angle = addendum_inv_angle + self._involute_func(addendum_inv_angle)
        tooth_angle = -angular_tooth_width - 2 * phi
        
        involute_1, involute_2 = [],[]
        n_inv = max(2, self.num_points[0])
        for i in range(n_inv):
            t = float(i) / (n_inv - 1)
            theta = t * (max_inv_angle - min_inv_angle) + min_inv_angle
            x_inv = base_radius * (math.cos(theta) + theta * math.sin(theta))
            y_inv = base_radius * (math.sin(theta) - theta * math.cos(theta))
            
            c_t, s_t = math.cos(tooth_angle), math.sin(tooth_angle)
            involute_2.append((x_inv * c_t - y_inv * s_t, x_inv * s_t + y_inv * c_t))
            involute_1.append((x_inv, -y_inv))
            
        upper_arc =[]
        n_up = max(2, self.num_points[1])
        inv_at_ded = self._involute_func(dedendum_inv_angle)
        start_u, end_u = -inv_at_ded, tooth_angle + inv_at_ded
        for i in range(n_up):
            t = float(i) / (n_up - 1)
            theta_arc = start_u + t * (end_u - start_u)
            upper_arc.append((dedendum_radius * math.cos(theta_arc), dedendum_radius * math.sin(theta_arc)))
            
        lower_arc_1, lower_arc_2 = [],[]
        start_l = tooth_angle + self._involute_func(addendum_inv_angle)
        end_l = -angular_tooth_width * 2 - self._involute_func(addendum_inv_angle)
        angular_width_lower = end_l - start_l
        
        h_points = max(2, self.num_points[2] // 2)
        for i in range(h_points):
            t = float(i) / (h_points - 1)
            theta_arc1 = start_l + t * angular_width_lower / 2
            theta_arc2 = -self._involute_func(addendum_inv_angle) - t * angular_width_lower / 2
            
            r_max = max(addendum_radius, base_radius)
            lower_arc_1.append((r_max * math.cos(theta_arc1), r_max * math.sin(theta_arc1)))
            lower_arc_2.append((r_max * math.cos(theta_arc2), r_max * math.sin(theta_arc2)))
            
        external_arc =[]
        n_ext = max(2, self.num_points[3])
        start_e = -self._involute_func(addendum_inv_angle) - angular_width_lower / 2
        end_e = start_l + angular_width_lower / 2
        for i in range(n_ext):
            t = float(i) / (n_ext - 1)
            theta_arc = start_e + t * (end_e - start_e)
            external_arc.append(((dedendum_radius + self.thickness) * math.cos(theta_arc), 
                                 (dedendum_radius + self.thickness) * math.sin(theta_arc)))

        rotation_angle = -tooth_angle / 2
        return {
            'involute_1':  self._rotate_points(involute_1, rotation_angle),
            'upper_arc':   self._rotate_points(upper_arc, rotation_angle),
            'involute_2':  self._rotate_points(involute_2, rotation_angle),
            'lower_arc_1': self._rotate_points(lower_arc_1, rotation_angle),
            'lower_arc_2': self._rotate_points(lower_arc_2, rotation_angle),
            'external_arc':self._rotate_points(external_arc, rotation_angle),
            'parameters': {'pitch_radius': pitch_radius}
        }


# ==============================================================================
# TEST SCENE
# ==============================================================================
class GearScene(Scene):
    def construct(self):
        # 1. Gear Generation
        module = 0.25 
        
        gear_center = InvoluteGear(
            z=8, m=module, 
            color=BLUE, stroke_width=2, 
            fill_opacity=0.7, fill_color=BLUE_E,
            tooth_phase=0
        )
        
        gear_right = InvoluteGear(
            z=12, m=module, 
            color=ORANGE, stroke_width=2, 
            fill_opacity=0.7, fill_color=ORANGE,
            tooth_phase=0.5
        )
        
        ring_gear = InvoluteGear(
            z=36, m=module, internal=True, thickness=0.5,
            color=WHITE, stroke_width=2,
            fill_opacity=0.3, fill_color=GRAY
        )

        # 2. Perfect Mathematical Positioning
        pr1 = gear_center.params['pitch_radius']
        pr2 = gear_right.params['pitch_radius']
        pr3 = ring_gear.params['pitch_radius']
        
        gear_right.shift(RIGHT * (pr1 + pr2))

        ring_gear.move_to(gear_right)
        ring_gear.shift(LEFT*(pr3-pr2))
        
        # Perfect mathematical offsets for meshing
        gear_center.rotate(math.pi / gear_center.z)  
        gear_right.rotate(math.pi / gear_right.z)

        # 3. Animation Sequence
        self.play(DrawBorderThenFill(ring_gear, run_time=2))
        self.play(FadeIn(gear_center, scale=0.5), FadeIn(gear_right, scale=0.5))
        
        # Update logic based on physical gear ratios
        def update_gear_right(g, dt):
            g.rotate(-dt * (gear_center.z / gear_right.z), about_point=gear_right.get_center())

        def update_ring(g, dt):
            g.rotate(-dt * (gear_center.z / ring_gear.z), about_point=ring_gear.get_center())

        def update_center(g,dt):
            g.rotate(dt, about_point=gear_center.get_center())

        gear_right.add_updater(update_gear_right)
        ring_gear.add_updater(update_ring)
        gear_center.add_updater(update_center)
        
        self.wait(10)
        # self.play(Rotate(gear_center, angle=PI * 2, run_time=6, rate_func=linear))
        
        gear_right.clear_updaters()
        ring_gear.clear_updaters()
        gear_center.clear_updaters()
        self.wait(1)