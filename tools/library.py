"""Master exercise library for The White Lotus Training Arc.

Each entry: id, name, element, category, equipment, cues (2-3 one-line coaching cues),
optional desc (short how-to), and an image source:
  fedb   -> free-exercise-db id (public domain photos, start + finish frames)
  search -> no exact DB match; searched on Wikimedia Commons / Pexels / Unsplash (see image_sources.json)
  pict   -> pictogram used for the illustrated placeholder if no correct photo exists

build_data.py only exports the exercises the schedule actually references.
"""

EX = {}


def E(id, name, element, category, equipment, cues, fedb=None, frame=1, desc=None,
      pict=None, search=None):
    assert id not in EX, f"duplicate exercise id {id}"
    assert 2 <= len(cues) <= 3, id
    EX[id] = dict(id=id, name=name, element=element, category=category,
                  equipment=equipment, cues=list(cues), fedb=fedb, frame=frame,
                  desc=desc, pict=pict, search=search)


# ---------------------------------------------------------------- EARTH: squat patterns
E("back-squat", "Barbell Back Squat", "earth", "Strength", "Barbell", [
    "Big breath into the brace, then sit straight down between your hips.",
    "Screw your feet into the floor; knees chase your pinky toes.",
    "Drive up chest-first so hips and shoulders rise together.",
], fedb="Barbell_Full_Squat")
E("front-squat", "Front Squat", "earth", "Strength", "Barbell", [
    "Elbows high, bar on the shelf; fingertips only hold it.",
    "Sit tall and deep; your torso stays vertical like a stone pillar.",
    "Knees forward, drive up through the whole foot.",
], fedb="Front_Squat_Clean_Grip")
E("box-squat", "Box Squat", "earth", "Strength", "Barbell", [
    "Sit back to the box and stay tight; no plopping.",
    "Pause with the brace on, then explode off the box.",
], fedb="Box_Squat")
E("goblet-squat", "Goblet Squat", "earth", "Strength", "Kettlebell / Dumbbell", [
    "Elbows inside the knees at the bottom; pry the hips open.",
    "Bell tight to the chest, heels heavy, chest proud.",
], fedb="Goblet_Squat")
E("zercher-squat", "Zercher Squat", "earth", "Strength", "Barbell", [
    "Bar in the elbow crease, hands together, hug it to your torso.",
    "Stay upright and brace hard; the bar wants to fold you forward.",
], fedb="Zercher_Squats")
E("overhead-squat", "Overhead Squat", "earth", "Olympic", "Barbell", [
    "Snatch grip, press up into the bar, armpits facing forward.",
    "Sit down slowly and stay balanced over mid-foot.",
], fedb="Overhead_Squat")
E("hack-squat", "Hack Squat (Machine)", "earth", "Strength", "Machine", [
    "Feet mid-platform; let the knees travel forward fully.",
    "Three seconds down, drive up without slamming the lockout.",
], fedb="Hack_Squat")
E("leg-press", "Leg Press", "earth", "Strength", "Machine", [
    "Lower back stays glued to the pad; stop before it peels.",
    "Push through the whole foot, smooth reps, no slamming.",
], fedb="Leg_Press")
E("jump-squat", "Barbell Jump Squat", "earth", "Power", "Barbell", [
    "Light load (20-30% of your squat); every rep is max height.",
    "Quick dip, explode, land soft and reset before the next rep.",
], fedb="Weighted_Jump_Squat")
E("kneeling-jump-squat", "Kneeling Jump to Squat", "earth", "Power", "Bodyweight / Barbell", [
    "Sit back to your heels, then snap the hips to land in a squat.",
    "Pure hip power: stick the landing with flat feet.",
], fedb="Kneeling_Jump_Squat")
E("spanish-squat", "Spanish Squat (Band Isometric)", "earth", "Resilience", "Heavy band", [
    "Band behind the knees; sit back with shins vertical.",
    "Hold the burn and breathe; this is patellar-tendon armor.",
], pict="squat", desc="Loop a heavy band around a rack behind your knees, lean back into it and sit to a half squat with vertical shins. Hold.")

# ---------------------------------------------------------------- EARTH: hinges
E("trap-bar-deadlift", "Trap Bar Deadlift", "earth", "Strength", "Trap bar", [
    "Push the floor away and let hips and knees open together.",
    "Lats tight, chest up, stand up fast.",
], fedb="Trap_Bar_Deadlift")
E("deadlift", "Conventional Deadlift", "earth", "Strength", "Barbell", [
    "Bar over mid-foot; pull the slack out before it leaves the floor.",
    "Push the floor, then drive the hips through and squeeze at lockout.",
    "Keep the bar dragging your legs the whole way up.",
], fedb="Barbell_Deadlift")
E("romanian-deadlift", "Romanian Deadlift", "earth", "Strength", "Barbell", [
    "Soft knees; push the hips back until the hamstrings bite.",
    "Bar drags the thighs, back flat, then snap the hips through.",
], fedb="Romanian_Deadlift")
E("snatch-grip-deadlift", "Snatch-Grip Deadlift", "earth", "Olympic", "Barbell", [
    "Wide grip, hips lower than a normal pull, chest up.",
    "Keep the bar close and push patiently through the floor.",
], fedb="Snatch_Deadlift")
E("good-morning", "Good Morning", "earth", "Strength", "Barbell", [
    "Hinge back with soft knees until your torso nears parallel.",
    "Stay braced; reverse by driving the hips forward.",
], fedb="Good_Morning")
E("hip-thrust", "Barbell Hip Thrust", "earth", "Strength", "Barbell", [
    "Chin tucked, ribs down; finish with the glutes, not the low back.",
    "Shins vertical at the top; pause one second and squeeze.",
], fedb="Barbell_Hip_Thrust")
E("single-leg-glute-bridge", "Single-Leg Glute Bridge", "earth", "Activation", "Bodyweight", [
    "Drive through the heel and keep the hips level like a tabletop.",
    "Pause at the top and feel the glute, not the hamstring.",
], fedb="Single_Leg_Glute_Bridge")
E("kb-swing", "Single-Arm Kettlebell Swing", "earth", "Power", "Kettlebell", [
    "Hike it back, then snap the hips; the arm is just a rope.",
    "Plank at the top: glutes tight, ribs down, bell floats.",
], fedb="One-Arm_Kettlebell_Swings")
E("pull-through", "Cable Pull-Through", "earth", "Strength", "Cable", [
    "Hinge back and let the cable pull you into the stretch.",
    "Drive the hips through and stand tall; don't lean back.",
], fedb="Pull_Through")
E("back-extension", "45° Back Extension", "water", "Posture", "Back-extension bench", [
    "Hinge at the hips over the pad with a neutral spine.",
    "Squeeze the glutes to rise; stop at a straight line, no over-arching.",
], fedb="Hyperextensions_Back_Extensions")
E("reverse-hyper", "Reverse Hyperextension", "earth", "Resilience", "Reverse hyper / bench", [
    "Swing the legs up with the glutes, not momentum.",
    "Let the spine decompress on the way down.",
], fedb="Reverse_Hyperextension")
E("nordic-curl", "Nordic Hamstring Curl", "earth", "Resilience", "Partner / anchor", [
    "Hips locked straight; lower as slowly as you can.",
    "Catch with your hands, push back up lightly, repeat.",
], fedb="Floor_Glute-Ham_Raise")
E("glute-ham-raise", "Glute-Ham Raise", "earth", "Strength", "GHD", [
    "Knees just behind the pad; curl up with the hamstrings, not the back.",
    "Squeeze the glutes the whole time to keep the hips extended.",
], fedb="Glute_Ham_Raise")
E("lying-leg-curl", "Lying Leg Curl", "earth", "Hypertrophy", "Machine", [
    "Hips pressed into the pad; curl fast, lower in three seconds.",
    "Pull the toes up toward the shins to bias the hamstrings.",
], fedb="Lying_Leg_Curls")
E("seated-leg-curl", "Seated Leg Curl", "earth", "Hypertrophy", "Machine", [
    "Lean forward slightly for a deeper hamstring stretch.",
    "Squeeze hard at the bottom, control on the way up.",
], fedb="Seated_Leg_Curl")
E("ball-leg-curl", "Stability Ball Leg Curl", "earth", "Resilience", "Stability ball", [
    "Bridge up first, then curl the ball in without dropping the hips.",
    "Slow on the way out; that's where hamstrings get armor.",
], fedb="Ball_Leg_Curl")
E("leg-extension", "Leg Extension", "earth", "Resilience", "Machine", [
    "Slow and smooth; this is tendon work for jumper's knee prevention.",
    "Pause two seconds at lockout, lower in three.",
], fedb="Leg_Extensions")

# ---------------------------------------------------------------- EARTH: single-leg & lateral
E("bulgarian-split-squat", "Bulgarian Split Squat", "earth", "Single-leg", "Dumbbells", [
    "Most of the weight on the front foot; the back foot is a kickstand.",
    "Drop the back knee straight down, drive up through the front heel.",
    "Lean the torso slightly forward to load the glute.",
], fedb="Split_Squat_with_Dumbbells")
E("barbell-bulgarian", "Barbell Bulgarian Split Squat", "earth", "Single-leg", "Barbell", [
    "Set the stance first; the front shin stays close to vertical.",
    "Control the descent and stand up through the front foot.",
], fedb="One_Leg_Barbell_Squat")
E("reverse-lunge", "Dumbbell Reverse Lunge", "earth", "Single-leg", "Dumbbells", [
    "Step back long and lower the back knee softly.",
    "Push through the front foot to return; stay tall.",
], fedb="Dumbbell_Rear_Lunge")
E("deficit-reverse-lunge", "Deficit Reverse Lunge", "earth", "Single-leg", "Barbell", [
    "Step back off the platform; knee kisses the floor.",
    "Drive up through the front foot. Big range builds big glutes.",
], fedb="Elevated_Back_Lunge")
E("walking-lunge", "Walking Lunge", "earth", "Single-leg", "Bodyweight / Sand", [
    "Long stride, back knee hovers, torso tall.",
    "On sand, punch each step into the ground; it fights back.",
], fedb="Bodyweight_Walking_Lunge")
E("db-walking-lunge", "Dumbbell Walking Lunge", "earth", "Single-leg", "Dumbbells", [
    "Smooth, continuous steps; don't pause at the top.",
    "Front knee tracks over the toes; push the floor behind you.",
], fedb="Dumbbell_Lunges")
E("crossover-lunge", "Crossover Reverse Lunge", "earth", "Single-leg", "Dumbbells", [
    "Step back and across like a curtsy; front knee stays over the foot.",
    "Feel the outer glute working to keep the pelvis level.",
], fedb="Crossover_Reverse_Lunge")
E("step-up", "Dumbbell Step-Up", "earth", "Single-leg", "Dumbbells + box", [
    "Whole foot on the box; drive through it with no push from the back leg.",
    "Stand fully tall at the top, then step down slowly.",
], fedb="Dumbbell_Step_Ups")
E("step-up-knee-drive", "Step-Up with Knee Drive", "earth", "Single-leg", "Box", [
    "Drive the free knee up like your approach takeoff.",
    "Finish tall on the box leg with hip, knee and ankle fully extended.",
], fedb="Step-up_with_Knee_Raise")
E("lateral-split-squat", "Lateral Split Squat", "earth", "Single-leg", "Barbell / Bodyweight", [
    "Sit into one hip with the other leg long and chest up.",
    "Push the floor sideways to return, just like a defensive step.",
], fedb="Barbell_Side_Split_Squat")
E("cossack-squat", "Cossack Squat", "earth", "Mobility", "Bodyweight / Kettlebell", [
    "Sit deep into one heel; the straight leg's toes point up.",
    "Shift side to side slowly while staying low.",
], pict="lunge", search="cossack squat",
  desc="Wide stance. Shift your weight and squat deep over one leg while the other stays straight with toes pointing up, then switch sides.")
E("single-leg-rdl", "Single-Leg RDL (Kettlebell)", "earth", "Single-leg", "Kettlebell", [
    "Hips square to the floor; reach the free heel back.",
    "Soft standing knee; hinge until the hamstring bites, then stand tall.",
], fedb="Kettlebell_One-Legged_Deadlift")
E("single-leg-box-squat", "Single-Leg Box Squat", "earth", "Single-leg", "Box", [
    "Sit back to the box on one leg, slow and controlled.",
    "Knee over toes; stand without pushing off the free foot.",
], fedb="Single-Leg_High_Box_Squat")
E("lunge-pass-through", "Kettlebell Lunge Pass-Through", "earth", "Single-leg", "Kettlebell", [
    "Pass the bell under the front leg each rep while staying upright.",
    "Control the depth; the back knee hovers.",
], fedb="Lunge_Pass_Through")

# ---------------------------------------------------------------- EARTH: calves, ankles, feet, adductors
E("standing-calf-raise", "Standing Calf Raise", "earth", "Resilience", "Machine", [
    "Full stretch at the bottom, pause, then rise as high as possible.",
    "Knees straight; drive through the big toe.",
], fedb="Standing_Calf_Raises")
E("seated-calf-raise", "Seated Calf Raise", "earth", "Resilience", "Machine", [
    "This hits the soleus, your sand-running engine.",
    "Pause two seconds in the stretch; no bouncing.",
], fedb="Seated_Calf_Raise")
E("db-calf-raise", "Dumbbell Calf Raise (Step)", "earth", "Resilience", "Dumbbells + step", [
    "Heels sink below the step, then rise onto the big toe.",
    "Three seconds down; the eccentric is where the armor forms.",
], fedb="Standing_Dumbbell_Calf_Raise")
E("tibialis-raise", "Tibialis Raise", "earth", "Resilience", "Wall / bodyweight", [
    "Back against the wall, heels forward; pull the toes to the shins.",
    "Pause at the top and lower slowly. Shins are an ankle's best friend.",
], pict="stand", search="tibialis raise",
  desc="Lean your back on a wall with heels about a foot out. Keep the legs straight and raise the toes toward the shins, then lower under control.")
E("ankle-circles", "Ankle Circles", "air", "Mobility", "Bodyweight", [
    "Big, slow circles; draw the biggest wheel you can.",
    "Both directions; feel every degree of the ankle.",
], fedb="Ankle_Circles")
E("jump-rope", "Jump Rope", "earth", "Elastic", "Rope", [
    "Quiet, quick contacts on the balls of the feet.",
    "Wrists turn the rope; elbows stay close.",
], fedb="Rope_Jumping")
E("pogo-hops", "Pogo Hops", "earth", "Elastic", "Bodyweight", [
    "Stiff ankles; bounce like the ground is hot.",
    "Minimal knee bend; let the Achilles do the work.",
], pict="jump", search="pogo jumps",
  desc="Small, rapid two-footed hops with nearly straight knees. Bounce off the balls of the feet with minimal ground contact.")
E("copenhagen-plank", "Copenhagen Plank", "earth", "Resilience", "Bench", [
    "Top leg on the bench, hips stacked, body in one straight line.",
    "Squeeze the bench with your inner thigh; no sagging.",
], pict="sideplank", search="copenhagen plank",
  desc="Side plank with your top leg resting on a bench (knee or ankle) and the bottom leg free. Lifts the hips using the adductors. Elite groin insurance for lateral movers.")
E("cable-hip-adduction", "Cable Hip Adduction", "earth", "Resilience", "Cable", [
    "Stand tall and sweep the leg across your body with control.",
    "Slow return; don't let the cable yank you open.",
], fedb="Cable_Hip_Adduction")
E("monster-walk", "Banded Monster Walk", "earth", "Activation", "Mini band", [
    "Stay low and wide; knees out against the band.",
    "Small steps with constant tension.",
], fedb="Monster_Walk")
E("side-plank", "Side Plank", "earth", "Core", "Bodyweight", [
    "Elbow under the shoulder, hips high, body in one line.",
    "Push the floor away and breathe behind the brace.",
], fedb="Side_Bridge")
E("barefoot-sand-walk", "Barefoot Sand Walk", "air", "Recovery", "Sand", [
    "Easy pace and nasal breathing; let the sand massage your feet.",
    "Walk tall and swing the arms loose. This is moving meditation.",
], pict="walk", search="barefoot walking on beach sand",
  desc="An easy walk barefoot on soft sand. Strengthens feet and ankles while flushing the legs.")

# ---------------------------------------------------------------- EARTH: Olympic & power
E("power-clean", "Power Clean", "earth", "Olympic", "Barbell", [
    "Push the floor through the first pull and keep the bar close.",
    "Violent hip extension, then pull yourself under with fast elbows.",
    "Catch high with soft knees and elbows up.",
], fedb="Power_Clean")
E("hang-clean", "Hang Clean", "earth", "Olympic", "Barbell", [
    "Hinge to mid-thigh, then jump and shrug.",
    "Whip the elbows around fast; meet the bar, don't chase it.",
], fedb="Hang_Clean")
E("hang-clean-below-knee", "Hang Clean (Below Knee)", "earth", "Olympic", "Barbell", [
    "Start below the knee; sweep the bar back into the hips.",
    "Stay over the bar until the hips open, then pull under.",
], fedb="Hang_Clean_-_Below_the_Knees")
E("power-clean-blocks", "Power Clean from Blocks", "earth", "Olympic", "Barbell + blocks", [
    "Set tight on the blocks; no slack, no hitching.",
    "Explode from a dead start and catch crisp.",
], fedb="Power_Clean_from_Blocks")
E("clean-pull", "Clean Pull", "earth", "Olympic", "Barbell", [
    "Same path as the clean: patient off the floor, explosive at the hip.",
    "Finish tall on the toes with a big shrug and long arms.",
], fedb="Clean_Pull")
E("power-snatch", "Power Snatch", "earth", "Olympic", "Barbell", [
    "Wide grip; brush the hip, then punch up and under.",
    "Lock the elbows in the catch with soft knees and chest up.",
], fedb="Power_Snatch")
E("hang-snatch", "Hang Snatch", "earth", "Olympic", "Barbell", [
    "Lats on, bar close; jump the bar off the hip.",
    "Fast turnover; punch the ceiling.",
], fedb="Hang_Snatch")
E("power-snatch-blocks", "Power Snatch from Blocks", "earth", "Olympic", "Barbell + blocks", [
    "Start above the knee and stay over the bar.",
    "Finish the extension before you pull under.",
], fedb="Power_Snatch_from_Blocks")
E("snatch-pull", "Snatch Pull", "earth", "Olympic", "Barbell", [
    "Snatch grip; keep the shoulders over the bar until the hip.",
    "Explode tall; elbows go up and out, bar stays close.",
], fedb="Snatch_Pull")
E("muscle-snatch", "Muscle Snatch", "earth", "Olympic", "Barbell", [
    "Don't re-bend the knees; pull high and turn the bar over.",
    "A shoulder-strength drill for a powerful arm swing.",
], fedb="Muscle_Snatch")
E("trap-bar-jump", "Trap Bar Jump", "earth", "Power", "Trap bar", [
    "Light load (20-40% of your trap bar max); jump as high as possible.",
    "Land soft, reset and breathe before every rep.",
], pict="jump", search="trap bar jump",
  desc="Hold a lightly loaded trap bar, dip and jump straight up, then land softly in an athletic stance.")
E("kb-snatch", "Single-Arm Kettlebell Snatch", "earth", "Power", "Kettlebell", [
    "Hike, snap the hips, punch through as the bell floats.",
    "Don't let the bell flop onto your wrist.",
], fedb="One-Arm_Kettlebell_Snatch")

# ---------------------------------------------------------------- EARTH: plyometrics & speed
E("box-jump", "Box Jump", "earth", "Plyometric", "Plyo box", [
    "Arm swing, explode, land soft and quiet in a half squat.",
    "Step down. Save the knees for jumping, not landing.",
], fedb="Front_Box_Jump")
E("seated-box-jump", "Seated Box Jump", "earth", "Plyometric", "Bench + box", [
    "Sit on a bench, feet planted, explode straight onto the box.",
    "Pure concentric power with no countermovement.",
], fedb="Dumbbell_Seated_Box_Jump")
E("depth-jump", "Depth Jump to Box", "earth", "Plyometric", "Two boxes", [
    "Step off (don't jump off), touch, and rebound instantly.",
    "Minimal ground time. The floor is lava.",
], fedb="Depth_Jump_Leap")
E("hurdle-hops", "Hurdle Hops", "earth", "Plyometric", "Mini hurdles", [
    "Knees up fast; spend as little time on the ground as possible.",
    "Stay tall and rhythmic between hurdles.",
], fedb="Hurdle_Hops")
E("broad-jump", "Broad Jump", "earth", "Plyometric", "Bodyweight", [
    "Big arm swing; jump out, not up, and stick the landing.",
    "Land in an athletic stance and hold for two seconds.",
], fedb="Standing_Long_Jump")
E("lateral-broad-jump", "Lateral Broad Jump", "earth", "Plyometric", "Bodyweight", [
    "Load the outside hip and jump as far sideways as you can.",
    "Stick it balanced; the block move starts here.",
], fedb="Side_Standing_Long_Jump")
E("tuck-jump", "Tuck Jump", "earth", "Plyometric", "Bodyweight", [
    "Pull the knees to the chest at the top of each jump.",
    "Land on the balls of the feet and rebound immediately.",
], fedb="Knee_Tuck_Jump")
E("lateral-bound", "Lateral Bound", "earth", "Plyometric", "Bodyweight", [
    "Push off the outside leg and land on the other; stick it one second.",
    "Knee over toes on landing; absorb like a spring.",
], fedb="Lateral_Bound")
E("diagonal-bound", "Diagonal Bound", "earth", "Plyometric", "Bodyweight", [
    "Drive the knee forward and across; cover distance and height.",
    "Land balanced and go again rhythmically.",
], fedb="Alternate_Leg_Diagonal_Bound")
E("single-leg-hop", "Single-Leg Forward Hop", "earth", "Plyometric", "Cones", [
    "Hop and land on the same leg; quiet, stable landings.",
    "Drive the free knee to help the takeoff.",
], fedb="Single-Leg_Hop_Progression")
E("single-leg-lateral-hop", "Single-Leg Lateral Hop", "earth", "Plyometric", "Line / cone", [
    "Hop side to side over a line on one leg.",
    "Stiff ankle, level hips, eyes up.",
], fedb="Single-Leg_Lateral_Hop")
E("lateral-cone-hops", "Lateral Cone Hops", "earth", "Plyometric", "Cones", [
    "Two-footed hops sideways down the line of cones.",
    "Quick off the ground; knees up to clear.",
], fedb="Lateral_Cone_Hops")
E("lateral-box-jump", "Lateral Box Jump", "earth", "Plyometric", "Low box", [
    "Dip and jump sideways onto the box; land soft.",
    "Step down and reset; lateral power is volleyball power.",
], fedb="Lateral_Box_Jump")
E("split-jump", "Split Jump", "earth", "Plyometric", "Bodyweight", [
    "From a lunge, jump high and switch legs in the air.",
    "Land soft with the front knee over the foot.",
], fedb="Split_Jump")
E("cmj", "Countermovement Jump", "earth", "Plyometric", "Bodyweight", [
    "Fast dip, full arm swing, reach for the ceiling.",
    "Treat each rep like a max attempt, then reset.",
], fedb="Rocket_Jump")
E("single-leg-push-off", "Single-Leg Box Push-Off", "earth", "Plyometric", "Box", [
    "Drive through the foot on the box and get tall.",
    "Land on the same foot and go again; knee drive like takeoff.",
], fedb="Single_Leg_Push-off")
E("stride-jump-crossover", "Stride Jump Crossover", "earth", "Plyometric", "Box", [
    "Drive off the box foot, cross over, and land on the far side.",
    "Arms drive up; stay quick through the box.",
], fedb="Stride_Jump_Crossover")
E("side-hop-sprint", "Side Hop to Sprint", "earth", "Speed", "Cone / hurdle", [
    "Quick lateral hops, then explode into a sprint off the last one.",
    "React. The transition is the whole drill.",
], fedb="Side_Hop-Sprint")
E("carioca", "Carioca", "earth", "Warm-up", "Bodyweight", [
    "Quick hips; the back foot crosses behind with a high knee.",
    "Stay light and rhythmic, arms relaxed.",
], fedb="Carioca_Quick_Step")
E("fast-skips", "Fast Skips", "earth", "Warm-up", "Bodyweight", [
    "Low, quick skips that minimize air time.",
    "Punch the arms and stay on the balls of the feet.",
], fedb="Fast_Skipping")
E("wall-drill", "Wall Acceleration Drill", "earth", "Speed", "Wall", [
    "Lean at 45°, glutes on; drive the knee and punch the foot down.",
    "Straight line from ankle to ear. That's your acceleration angle.",
], fedb="Linear_Acceleration_Wall_Drill")
E("sprint-start", "3-Point Sprint Start", "earth", "Speed", "Line", [
    "Nose over the front knee, hips high; explode out low.",
    "First three steps are pushes, not reaches.",
], fedb="Linear_3-Part_Start_Technique")
E("sled-push", "Sled Push", "earth", "Conditioning", "Sled", [
    "Arms long, body at 45°, drive the knees.",
    "Short, powerful steps through the balls of the feet.",
], fedb="Sled_Push")
E("backward-sled-drag", "Backward Sled Drag", "earth", "Resilience", "Sled", [
    "Lean back and take short, fast steps. Knee-friendly quad burn.",
    "Stay on the balls of the feet the whole way.",
], fedb="Backward_Drag")
E("mountain-climbers", "Mountain Climbers", "earth", "Conditioning", "Bodyweight", [
    "Hands under the shoulders; drive the knees fast.",
    "Hips stay level. No sky-high butt.",
], fedb="Mountain_Climbers")
E("approach-jump", "Volleyball Approach Jump", "earth", "Sport", "Sand", [
    "Accelerate into the last two steps: left-right-left for righties.",
    "Big arm swing, plant the heels, turn speed into height.",
    "Long penultimate step, then a quick close. Swing both arms up hard.",
], pict="jump", search="beach volleyball spike jump",
  desc="Your full spike approach and jump without a ball (or with a toss). Maximal intent every rep.")
E("block-jump", "Block Jump", "earth", "Sport", "Sand / net", [
    "Hands high and in front; quick dip, press over the net.",
    "Land balanced and ready to move. No drifting.",
], pict="jump", search="beach volleyball block at net",
  desc="Stand at the net with hands at shoulder height, dip and jump straight up, pressing hands over the tape. Land in place.")
E("sand-sprint", "Sand Sprint", "earth", "Speed", "Sand", [
    "Drive the knees and punch the arms; sand rewards power.",
    "Short, quick steps for the first five meters.",
], pict="sprint", search="sprinting on beach sand",
  desc="Sprint on soft sand. Walk back for recovery. The sand cuts impact and doubles the effort.")
E("sand-jog", "Easy Sand Jog", "air", "Warm-up", "Sand", [
    "Easy pace, short strides, let the feet wake up.",
    "Breathe through the nose. If you can't chat, slow down.",
], pict="sprint", search="jogging on beach",
  desc="An easy jog on the sand to raise temperature and wake up feet and ankles.")
E("lateral-shuffle", "Lateral Shuffle", "earth", "Sport", "Sand", [
    "Low hips, wide base; push off the trail leg.",
    "Never cross your feet; eyes up like you're reading a hitter.",
], pict="shuffle", search="defensive slide shuffle drill",
  desc="Athletic stance, shuffle sideways without clicking the feet together. Stay low the whole way.")
E("backpedal-sprint", "Backpedal to Sprint", "earth", "Sport", "Sand", [
    "Quick backpedal with your chest over your toes.",
    "Open the hips on the cue and sprint. React, don't think.",
], pict="sprint",
  desc="Backpedal 5 m, then plant, open the hips and sprint forward 10 m, like chasing a shanked pass.")
E("bear-crawl", "Bear Crawl", "earth", "Conditioning", "Bodyweight", [
    "Knees hover an inch off the ground; opposite hand and foot move together.",
    "Keep the back flat enough to balance a cup of tea.",
], pict="crawl", search="bear crawl exercise",
  desc="On hands and feet with knees just off the ground, crawl forward with opposite hand and foot moving together.")

# ---------------------------------------------------------------- WATER: vertical pulls
E("weighted-pull-up", "Weighted Pull-Up", "water", "Strength", "Pull-up bar + belt", [
    "Start from a dead hang and pull the elbows down to the ribs.",
    "Chest to the bar; control the descent in two seconds.",
], fedb="Weighted_Pull_Ups")
E("pull-up", "Pull-Up", "water", "Strength", "Pull-up bar", [
    "Pack the shoulders, then drive the elbows to the back pockets.",
    "Full hang at the bottom every rep; no half-reps.",
], fedb="Pullups")
E("chin-up", "Chin-Up", "water", "Strength", "Pull-up bar", [
    "Palms facing you; pull the chest to the bar.",
    "Squeeze the biceps and lats together at the top.",
], fedb="Chin-Up")
E("neutral-pull-up", "Neutral-Grip Pull-Up", "water", "Strength", "V-handle / parallel bars", [
    "Neutral grip is shoulder-friendly; pull the sternum to the handles.",
    "Ribs down, no kipping, smooth tempo.",
], fedb="V-Bar_Pullup")
E("scap-pull-up", "Scapular Pull-Up", "water", "Shoulder health", "Pull-up bar", [
    "Straight arms; pull the shoulder blades down and back.",
    "Pause one second. This wakes up the lower traps.",
], fedb="Scapular_Pull-Up")
E("lat-pulldown", "Wide-Grip Lat Pulldown", "water", "Hypertrophy", "Cable", [
    "Pull the bar to the upper chest; lead with the elbows.",
    "Lean back slightly and feel the lats stretch at the top.",
], fedb="Wide-Grip_Lat_Pulldown")
E("close-grip-pulldown", "Close-Grip Pulldown", "water", "Hypertrophy", "Cable", [
    "Tall chest; pull the handle to the sternum.",
    "Full stretch overhead between reps.",
], fedb="Close-Grip_Front_Lat_Pulldown")
E("v-bar-pulldown", "V-Bar Pulldown", "water", "Hypertrophy", "Cable", [
    "Drive the elbows down and in; squeeze the lats.",
    "Control the bar back up for three seconds.",
], fedb="V-Bar_Pulldown")
E("underhand-pulldown", "Underhand Pulldown", "water", "Hypertrophy", "Cable", [
    "Supinated grip, elbows tight to the body.",
    "Pull to the upper chest and squeeze for one second.",
], fedb="Underhand_Cable_Pulldowns")
E("single-arm-pulldown", "Single-Arm Lat Pulldown", "water", "Hypertrophy", "Cable", [
    "Pull the elbow to the hip with a slight torso crunch.",
    "Let the shoulder blade rise fully at the top.",
], fedb="One_Arm_Lat_Pulldown")
E("straight-arm-pulldown", "Straight-Arm Pulldown", "water", "Hypertrophy", "Cable", [
    "Arms long, sweep the bar to the thighs with the lats.",
    "Ribs down; don't let the low back arch.",
], fedb="Straight-Arm_Pulldown")

# ---------------------------------------------------------------- WATER: horizontal pulls
E("barbell-row", "Barbell Bent-Over Row", "water", "Strength", "Barbell", [
    "Hinge to about 45°, brace, and row the bar to the lower ribs.",
    "No hip-humping; the torso angle stays locked.",
], fedb="Bent_Over_Barbell_Row")
E("reverse-grip-row", "Reverse-Grip Barbell Row", "water", "Strength", "Barbell", [
    "Underhand grip; row to the belly button with elbows tight.",
    "Squeeze the shoulder blades together at the top.",
], fedb="Reverse_Grip_Bent-Over_Rows")
E("t-bar-row", "T-Bar Row", "water", "Strength", "Landmine / T-bar", [
    "Chest proud, hinge locked; drive the elbows back.",
    "Pause at the chest and lower under control.",
], fedb="T-Bar_Row_with_Handle")
E("chest-supported-t-bar", "Chest-Supported T-Bar Row", "water", "Hypertrophy", "Machine", [
    "Chest stays on the pad; pull with the back, not momentum.",
    "Full stretch at the bottom, hard squeeze at the top.",
], fedb="Lying_T-Bar_Row")
E("db-row", "Single-Arm Dumbbell Row", "water", "Strength", "Dumbbell + bench", [
    "Row the dumbbell to the hip pocket, not the armpit.",
    "Square shoulders; let the lat stretch at the bottom.",
], fedb="One-Arm_Dumbbell_Row")
E("incline-db-row", "Chest-Supported Dumbbell Row", "water", "Posture", "Dumbbells + incline bench", [
    "Chest on the incline; row and pause with the shoulder blades squeezed.",
    "Lead with the elbows and keep the neck long.",
], fedb="Dumbbell_Incline_Row")
E("seated-cable-row", "Seated Cable Row", "water", "Hypertrophy", "Cable", [
    "Sit tall and pull the handle to the belly; elbows skim the ribs.",
    "Reach forward and let the shoulder blades spread before each rep.",
], fedb="Seated_Cable_Rows")
E("single-arm-cable-row", "Single-Arm Cable Row", "water", "Athletic", "Cable", [
    "Row with a little rotation, like drawing back for a swing.",
    "Hips square; let the shoulder reach forward at full stretch.",
], fedb="Seated_One-arm_Cable_Pulley_Rows")
E("inverted-row", "Inverted Row", "water", "Strength", "Bar / Smith", [
    "Body in a plank; pull the chest to the bar.",
    "Squeeze the shoulder blades, then lower slowly.",
], fedb="Inverted_Row")
E("ring-row", "Suspension Row", "water", "Posture", "Rings / TRX", [
    "Plank body, pull the hands to the ribs, thumbs rotate out.",
    "Walk the feet forward to make it harder.",
], fedb="Inverted_Row_with_Straps")
E("meadows-row", "Landmine Single-Arm Row", "water", "Strength", "Landmine", [
    "Staggered stance, hinge; row the bar end to the hip.",
    "Big stretch at the bottom, no torso twist.",
], fedb="One-Arm_Long_Bar_Row")
E("seal-row", "Lying Barbell Row", "water", "Strength", "Barbell + high bench", [
    "Chest pinned to the bench; there's no cheating here.",
    "Pull the bar to the bench and pause one second.",
], fedb="Lying_Cambered_Barbell_Row")
E("renegade-row", "Renegade Row", "water", "Athletic", "Kettlebells / dumbbells", [
    "Wide feet, plank tight; row without letting the hips rotate.",
    "Opposite hand pushes the floor away.",
], fedb="Alternating_Renegade_Row")
E("high-row", "Kneeling High-Pulley Row", "water", "Posture", "Cable", [
    "Pull to the upper chest with elbows wide and high.",
    "Finish with the shoulder blades set down and back.",
], fedb="Kneeling_High_Pulley_Row")
E("rack-pull", "Rack Pull", "water", "Strength", "Barbell + rack", [
    "Bar just below the knee; push the hips through to lockout.",
    "Shoulders back at the top; don't hyperextend.",
], fedb="Rack_Pulls")

# ---------------------------------------------------------------- WATER: scapular & shoulder health
E("face-pull", "Face Pull", "water", "Shoulder health", "Cable + rope", [
    "Pull to the eyebrows with elbows high and thumbs back.",
    "Finish like a double-biceps pose: rotate the hands back.",
], fedb="Face_Pull")
E("band-pull-apart", "Band Pull-Apart", "water", "Shoulder health", "Band", [
    "Arms straight; pull the band to the chest by squeezing the shoulder blades.",
    "Slow return. The rear delts are the hitting arm's brakes.",
], fedb="Band_Pull_Apart")
E("reverse-fly", "Chest-Supported Reverse Fly", "water", "Shoulder health", "Dumbbells + incline bench", [
    "Chest on the incline, soft elbows; open the arms like wings.",
    "Lead with the pinkies and pause at the top.",
], fedb="Reverse_Flyes")
E("cable-rear-delt-fly", "Cable Rear Delt Fly", "water", "Hypertrophy", "Cable", [
    "Cross the cables and sweep back wide at shoulder height.",
    "No shrugging; the neck stays long.",
], fedb="Cable_Rear_Delt_Fly")
E("reverse-machine-fly", "Reverse Pec Deck", "water", "Hypertrophy", "Machine", [
    "Chest on the pad; sweep the handles back with straight arms.",
    "Pause and squeeze the rear delts, then control the return.",
], fedb="Reverse_Machine_Flyes")
E("incline-reverse-fly-er", "Incline Reverse Fly + External Rotation", "water", "Shoulder health", "Dumbbells + incline bench", [
    "Fly out, then rotate the forearms up at the top.",
    "Light weight, perfect positions. This protects the serve.",
], fedb="Reverse_Flyes_With_External_Rotation")
E("scaption", "Dumbbell Scaption", "water", "Shoulder health", "Light dumbbells", [
    "Thumbs up and raise in a Y, about 30° in front of you.",
    "Stop at shoulder height; smooth and controlled.",
], fedb="Dumbbell_Scaption")
E("serratus-raise", "Incline Serratus Shoulder Raise", "water", "Shoulder health", "Dumbbells + incline bench", [
    "Arms locked; punch the dumbbells up using only the shoulder blades.",
    "Feel the serratus wrap the ribs. A healthy scapula makes a healthy shoulder.",
], fedb="Dumbbell_Incline_Shoulder_Raise")
E("external-rotation-db", "Side-Lying External Rotation", "water", "Shoulder health", "Light dumbbell", [
    "Elbow pinned to the side at 90°; rotate the forearm up.",
    "Slow both ways. If you need momentum, it's too heavy.",
], fedb="External_Rotation")
E("external-rotation-cable", "Cable External Rotation", "water", "Shoulder health", "Cable", [
    "Towel under the elbow and rotate out without the elbow drifting.",
    "Two seconds out, three seconds back.",
], fedb="External_Rotation_with_Cable")
E("external-rotation-band", "Band External Rotation", "water", "Shoulder health", "Band", [
    "Elbow at your side; rotate out against the band.",
    "Keep the shoulder blade set down and back.",
], fedb="External_Rotation_with_Band")
E("internal-rotation-band", "Band Internal Rotation", "water", "Shoulder health", "Band", [
    "Elbow at your side; rotate in with control.",
    "Balance the cuff. Both directions matter for a hitter.",
], fedb="Internal_Rotation_with_Band")
E("cuban-press", "Cuban Press", "fire", "Shoulder health", "Light dumbbells / barbell", [
    "Upright row to 90°, rotate up, then press overhead.",
    "Featherweight load; this is cuff and posture work.",
], fedb="Cuban_Press")
E("superman", "Superman Hold", "water", "Posture", "Bodyweight", [
    "Lift the arms and legs a few inches and squeeze the glutes.",
    "Long neck; reach out, not up.",
], fedb="Superman")
E("shrug", "Barbell Shrug", "water", "Strength", "Barbell", [
    "Straight up to the ears; pause one second.",
    "No rolling. Up and down only.",
], fedb="Barbell_Shrug")

# ---------------------------------------------------------------- WATER: rotational & athletic
E("med-ball-slam", "Med-Ball Overhead Slam", "water", "Power", "Slam ball", [
    "Reach tall onto the toes, then slam through the core.",
    "Throw it through the floor; hinge, catch, repeat.",
], fedb="Overhead_Slam")
E("one-arm-slam", "Single-Arm Med-Ball Slam", "water", "Power", "Slam ball", [
    "Reach tall like an attack, then whip down through the core.",
    "Alternate arms; the off-arm matters too.",
], fedb="One-Arm_Medicine_Ball_Slam")
E("scoop-throw", "Med-Ball Scoop Toss", "water", "Power", "Medicine ball", [
    "Load the hips low and throw the ball up and back with a full extension.",
    "Jump with it; triple extension is the goal.",
], fedb="Medicine_Ball_Scoop_Throw")
E("backward-throw", "Backward Med-Ball Throw", "water", "Power", "Medicine ball", [
    "Squat, then explode, launching the ball overhead behind you.",
    "Hips do the work; arms just steer.",
], fedb="Backward_Medicine_Ball_Throw")
E("overhead-throw", "Overhead Med-Ball Throw", "water", "Power", "Medicine ball", [
    "Reach the ball deep behind your head and throw with the whole body.",
    "Feels like a spike. Lead with the core and follow through.",
], fedb="Standing_Two-Arm_Overhead_Throw")
E("supine-one-arm-throw", "Supine Single-Arm Overhead Throw", "water", "Power", "Medicine ball", [
    "Arm fully back; sit up and throw like a quick attack.",
    "Light ball, fast arm. Speed is the goal.",
], fedb="Supine_One-Arm_Overhead_Throw")
E("rotational-pass", "Rotational Med-Ball Pass", "water", "Power", "Medicine ball + partner/wall", [
    "Rotate from the hips first, then the shoulders.",
    "Stay tall and athletic; catch and reload fast.",
], fedb="Medicine_Ball_Full_Twist")
E("woodchop", "Cable Woodchop", "water", "Core", "Cable", [
    "High to low across the body; pivot the back foot.",
    "Arms stay long, rotation comes from hips and torso.",
], fedb="Standing_Cable_Wood_Chop")
E("cable-lift", "Cable Low-to-High Lift", "water", "Core", "Cable", [
    "Low to high across the body, finishing tall.",
    "Brace first, then rotate; control the return.",
], fedb="Standing_Cable_Lift")
E("pallof-press", "Pallof Press", "water", "Core", "Cable / band", [
    "Press straight out and resist the rotation.",
    "Ribs down, glutes on, breathe behind the brace.",
], fedb="Pallof_Press")
E("pallof-rotation", "Pallof Press with Rotation", "water", "Core", "Cable", [
    "Press out, rotate away under control, return to center.",
    "Hips face forward; the torso does the rotating.",
], fedb="Pallof_Press_With_Rotation")
E("landmine-rotation", "Landmine 180", "water", "Core", "Landmine", [
    "Arms long; arc the bar hip to hip with a pivot.",
    "Rotate through the hips, not just the arms.",
], fedb="Landmine_180s")
E("russian-twist", "Russian Twist", "water", "Core", "Plate / med ball", [
    "Lean back, chest proud; rotate the ribs, not just the arms.",
    "Touch beside each hip with control.",
], fedb="Russian_Twist")
E("kb-windmill", "Kettlebell Windmill", "fire", "Shoulder health", "Kettlebell", [
    "Bell locked overhead, eyes on it; hinge sideways.",
    "Push the hips out and keep the top arm vertical.",
], fedb="Kettlebell_Windmill")
E("turkish-get-up", "Turkish Get-Up", "fire", "Shoulder health", "Kettlebell", [
    "Eyes on the bell; arm vertical at every stage.",
    "Slow is smooth. Earn every position.",
], fedb="Kettlebell_Turkish_Get-Up_Lunge_style")
E("kb-halo", "Kettlebell Halo", "fire", "Mobility", "Kettlebell", [
    "Circle the bell tight around your head, both directions.",
    "Ribs down; move the shoulders, not the lower back.",
], pict="stand", search="kettlebell halo",  # DB entry Kettlebell_Halo has no photos
  desc="Hold a light kettlebell upside-down by the horns and circle it slowly around your head, keeping it close.")
E("bottoms-up-clean", "Bottoms-Up Kettlebell Clean", "fire", "Shoulder health", "Kettlebell", [
    "Crush the handle and clean the bell upside-down to the shoulder.",
    "Balance it. The cuff lights up to keep it steady.",
], fedb="Bottoms-Up_Clean_From_The_Hang_Position")
E("farmers-walk", "Farmer's Walk", "water", "Carry", "Dumbbells / handles", [
    "Tall posture, shoulders packed, short quick steps.",
    "Crush the handles; grip is shoulder health.",
], fedb="Farmers_Walk")
E("suitcase-deadlift", "Suitcase Deadlift", "water", "Core", "Barbell or dumbbell, one hand", [
    "One weight at your side; don't let the torso tilt.",
    "Hinge and stand like the weight isn't there.",
], fedb="One-Arm_Side_Deadlift")
E("single-arm-hang", "Single-Arm Dead Hang", "water", "Shoulder health", "Pull-up bar", [
    "Hang long and let the shoulder decompress.",
    "Breathe slowly; switch hands before the grip fails.",
], fedb="One_Handed_Hang")
E("sledgehammer", "Sledgehammer Tire Strikes", "water", "Conditioning", "Sledgehammer + tire", [
    "Slide the top hand down as the hammer falls; switch sides.",
    "Power comes from the hips and core like an attack swing.",
], fedb="Sledgehammer_Swings")
E("battle-ropes", "Battle Ropes", "fire", "Conditioning", "Ropes", [
    "Athletic stance, fast alternating waves from the shoulders.",
    "Breathe. Keep the waves all the way to the anchor.",
], fedb="Battling_Ropes")

# ---------------------------------------------------------------- WATER: biceps & forearms
E("barbell-curl", "Barbell Curl", "water", "Hypertrophy", "Barbell", [
    "Elbows pinned; curl without swinging the hips.",
    "Squeeze at the top and lower in two seconds.",
], fedb="Barbell_Curl")
E("ez-curl", "EZ-Bar Curl", "water", "Hypertrophy", "EZ bar", [
    "Wrist-friendly grip; full range every rep.",
    "Don't let the elbows drift forward at the top.",
], fedb="EZ-Bar_Curl")
E("drag-curl", "Drag Curl", "water", "Hypertrophy", "Barbell", [
    "Drag the bar up the torso as the elbows travel back.",
    "Squeeze hard at the top; slow on the way down.",
], fedb="Drag_Curl")
E("hammer-curl", "Hammer Curl", "water", "Hypertrophy", "Dumbbells", [
    "Neutral grip; curl like you're lifting a hammer.",
    "Builds the brachialis and forearm, an elbow's armor.",
], fedb="Hammer_Curls")
E("cross-body-hammer", "Cross-Body Hammer Curl", "water", "Hypertrophy", "Dumbbells", [
    "Curl across the body toward the opposite shoulder.",
    "Control the descent; no swinging.",
], fedb="Cross_Body_Hammer_Curl")
E("rope-hammer-curl", "Cable Rope Hammer Curl", "water", "Hypertrophy", "Cable + rope", [
    "Pin the elbows and pull the rope ends apart at the top.",
    "Constant tension, slow eccentric.",
], fedb="Cable_Hammer_Curls_-_Rope_Attachment")
E("incline-curl", "Incline Dumbbell Curl", "water", "Hypertrophy", "Dumbbells + incline bench", [
    "Arms hang behind you; curl from the full stretch.",
    "Keep the shoulders back against the bench.",
], fedb="Incline_Dumbbell_Curl")
E("preacher-curl", "Preacher Curl", "water", "Hypertrophy", "EZ bar + preacher bench", [
    "Armpits on the pad; don't bounce out of the bottom.",
    "Slow down the last third of each rep.",
], fedb="Preacher_Curl")
E("cable-curl", "Cable Curl", "water", "Hypertrophy", "Cable", [
    "Step back for tension at the bottom; elbows still.",
    "Squeeze and hold the top for one second.",
], fedb="Standing_Biceps_Cable_Curl")
E("spider-curl", "Spider Curl", "water", "Hypertrophy", "Dumbbells / EZ bar", [
    "Chest on the incline, arms hanging straight down.",
    "Curl and squeeze hard; no shoulder swing.",
], fedb="Spider_Curl")
E("concentration-curl", "Concentration Curl", "water", "Hypertrophy", "Dumbbell", [
    "Elbow braced on the inner thigh; curl to the shoulder.",
    "Supinate hard at the top.",
], fedb="Concentration_Curls")
E("zottman-curl", "Zottman Curl", "water", "Resilience", "Dumbbells", [
    "Curl palms-up, rotate at the top, lower palms-down slowly.",
    "Forearm and elbow insurance for the hitting arm.",
], fedb="Zottman_Curl")
E("reverse-curl", "Reverse Barbell Curl", "water", "Resilience", "Barbell / EZ bar", [
    "Overhand grip; elbows pinned, wrists neutral.",
    "Lower slowly. Your forearms will file a complaint.",
], fedb="Reverse_Barbell_Curl")
E("high-cable-curl", "Overhead Cable Curl", "water", "Hypertrophy", "Cable", [
    "Arms out at shoulder height; curl the handles toward your ears.",
    "Keep the upper arms still and level.",
], fedb="Overhead_Cable_Curl")  # DB "High_Cable_Curls" photo shows a lying variation, not the standing one
E("wrist-roller", "Wrist Roller", "water", "Resilience", "Wrist roller", [
    "Arms out front; roll the weight up and slowly back down.",
    "Forearms built for a thousand passes.",
], fedb="Wrist_Roller")
E("wrist-curl", "Barbell Wrist Curl", "water", "Resilience", "Barbell + bench", [
    "Forearms on the bench, let the bar roll to the fingertips.",
    "Curl the wrist up and squeeze.",
], fedb="Palms-Up_Barbell_Wrist_Curl_Over_A_Bench")

# ---------------------------------------------------------------- FIRE: chest
E("bench-press", "Barbell Bench Press", "fire", "Strength", "Barbell", [
    "Shoulder blades pinned, feet driving; bar to the lower chest.",
    "Bend the bar and push yourself away from it.",
    "Touch soft, then drive explosively. Same groove every rep.",
], fedb="Barbell_Bench_Press_-_Medium_Grip")
E("incline-bench", "Incline Barbell Bench Press", "fire", "Strength", "Barbell", [
    "Low incline (about 30°); bar to the upper chest.",
    "Elbows about 45° from the torso; press up and slightly back.",
], fedb="Barbell_Incline_Bench_Press_-_Medium_Grip")
E("db-bench", "Dumbbell Bench Press", "fire", "Hypertrophy", "Dumbbells", [
    "Deep stretch at the bottom, press up and slightly in.",
    "Wrists stacked over the elbows.",
], fedb="Dumbbell_Bench_Press")
E("neutral-db-bench", "Neutral-Grip Dumbbell Press", "fire", "Shoulder health", "Dumbbells", [
    "Palms facing each other is the shoulder-friendly pressing path.",
    "Tuck the elbows and press smoothly.",
], fedb="Dumbbell_Bench_Press_with_Neutral_Grip")
E("incline-db-press", "Incline Dumbbell Press", "fire", "Hypertrophy", "Dumbbells", [
    "Low incline; let the dumbbells sink to a full stretch.",
    "Press up and together without clanging.",
], fedb="Incline_Dumbbell_Press")
E("neutral-incline-db", "Neutral-Grip Incline Press", "fire", "Hypertrophy", "Dumbbells", [
    "Palms in, elbows tucked; easy on the shoulders, hard on the chest.",
    "Three seconds down, drive up.",
], fedb="Hammer_Grip_Incline_DB_Bench_Press")
E("close-grip-bench", "Close-Grip Bench Press", "fire", "Strength", "Barbell", [
    "Hands just inside shoulder width; elbows tucked.",
    "Touch the lower chest and drive with the triceps.",
], fedb="Close-Grip_Barbell_Bench_Press")
E("floor-press", "Barbell Floor Press", "fire", "Strength", "Barbell", [
    "Triceps touch the floor softly; pause, then press.",
    "No bounce. Pure lockout strength.",
], fedb="Floor_Press")
E("db-floor-press", "Dumbbell Floor Press", "fire", "Shoulder health", "Dumbbells", [
    "The floor limits range, which is easy on the shoulder.",
    "Pause at the bottom, press with a neutral wrist.",
], fedb="Dumbbell_Floor_Press")
E("pin-press", "Pin Press", "fire", "Strength", "Barbell + rack", [
    "Bar starts on pins an inch off the chest; dead stop.",
    "Drive explosively off the pins.",
], fedb="Pin_Presses")
E("band-bench", "Banded Speed Bench", "fire", "Power", "Barbell + bands", [
    "Light bar with bands; accelerate through the whole rep.",
    "Fast down (controlled), faster up.",
], fedb="Bench_Press_-_With_Bands")
E("chest-dip", "Weighted Chest Dip", "fire", "Strength", "Dip bars + belt", [
    "Lean forward slightly and lower until the shoulders are just below the elbows.",
    "Press up and squeeze the chest; no shoulder shrug.",
], fedb="Dips_-_Chest_Version")
E("triceps-dip", "Triceps Dip", "fire", "Hypertrophy", "Dip bars", [
    "Torso upright, elbows back; lower to 90°.",
    "Lock out hard with the triceps.",
], fedb="Dips_-_Triceps_Version")
E("push-up", "Push-Up", "fire", "Strength", "Bodyweight", [
    "Plank body; chest to the floor, elbows at 45°.",
    "Push the floor away and spread the shoulder blades at the top.",
], fedb="Pushups")
E("feet-elevated-push-up", "Feet-Elevated Push-Up", "fire", "Hypertrophy", "Bench", [
    "Feet on the bench, body straight; chest toward the floor.",
    "Upper-chest builder. Slow down, fast up.",
], fedb="Push-Ups_With_Feet_Elevated")
E("close-push-up", "Close-Grip Push-Up", "fire", "Hypertrophy", "Bodyweight", [
    "Hands under the shoulders, elbows brushing the ribs.",
    "Triceps finish; full lockout each rep.",
], fedb="Push-Ups_-_Close_Triceps_Position")
E("plyo-push-up", "Plyo Push-Up", "fire", "Power", "Bodyweight", [
    "Explode so the hands leave the floor; land soft and rebound.",
    "Rigid plank. Power from the chest, not a hip flop.",
], fedb="Plyo_Push-up")
E("drop-push-up", "Depth Drop Push-Up", "fire", "Power", "Two low boxes", [
    "Drop from the boxes, absorb, and explode back up.",
    "Minimal ground time; stay stiff through the trunk.",
], fedb="Drop_Push")
E("kb-plyo-push-up", "Kettlebell Plyo Push-Up", "fire", "Power", "Kettlebell", [
    "Push off the bell, switch hands in the air, land soft.",
    "Fast and controlled with a tight plank.",
], fedb="Plyo_Kettlebell_Pushups")
E("chest-pass", "Med-Ball Chest Pass", "fire", "Power", "Medicine ball", [
    "Step and throw from the chest as hard as you can.",
    "Thumbs down on the follow-through; full arm extension.",
], fedb="Medicine_Ball_Chest_Pass")
E("kneeling-chest-push", "Kneeling Med-Ball Chest Push", "fire", "Power", "Medicine ball", [
    "From tall kneeling, launch the ball out and fall into a push-up.",
    "The hips fire first, then the arms punch.",
], fedb="Chest_Push_single_response")
E("supine-chest-throw", "Supine Med-Ball Chest Throw", "fire", "Power", "Medicine ball", [
    "From your back, punch the ball straight up as high as possible.",
    "Catch, absorb, and throw again immediately.",
], fedb="Supine_Chest_Throw")
E("chest-push-sprint", "Med-Ball Chest Push to Sprint", "fire", "Power", "Medicine ball + sand", [
    "Throw from a low athletic stance and chase it immediately.",
    "Transfer push power into acceleration.",
], fedb="Chest_Push_with_Run_Release")
E("cable-crossover", "Cable Crossover", "fire", "Hypertrophy", "Cable", [
    "Slight forward lean; hug a tree and cross the hands.",
    "Big stretch, controlled squeeze.",
], fedb="Cable_Crossover")
E("low-cable-fly", "Low-to-High Cable Fly", "fire", "Hypertrophy", "Cable", [
    "Sweep up from the hips to eye level.",
    "Upper-chest focus; keep a soft bend in the elbows.",
], fedb="Low_Cable_Crossover")
E("incline-cable-fly", "Incline Cable Fly", "fire", "Hypertrophy", "Cable + incline bench", [
    "Arms open wide, chest up, slight elbow bend.",
    "Squeeze the hands together over the upper chest.",
], fedb="Incline_Cable_Flye")
E("db-fly", "Dumbbell Fly", "fire", "Hypertrophy", "Dumbbells", [
    "Open wide with soft elbows until you feel the stretch.",
    "Bring them up like hugging a barrel.",
], fedb="Dumbbell_Flyes")
E("pec-deck", "Pec Deck", "fire", "Hypertrophy", "Machine", [
    "Shoulders back; close the handles with the chest.",
    "Pause at full contraction.",
], fedb="Butterfly")
E("svend-press", "Svend Press", "fire", "Hypertrophy", "Plates", [
    "Squeeze the plates together and press straight out.",
    "Keep crushing the plates the whole time.",
], fedb="Svend_Press")
E("cable-chest-press", "Standing Cable Chest Press", "fire", "Athletic", "Cable", [
    "Staggered stance; press forward without letting the cables twist you.",
    "Core anti-rotation plus press, like a block-to-transition push.",
], fedb="Standing_Cable_Chest_Press")

# ---------------------------------------------------------------- FIRE: shoulders & overhead
E("ohp", "Standing Overhead Press", "fire", "Strength", "Barbell", [
    "Glutes and abs tight; press the bar up and slightly back.",
    "Head through the window at the top; full lockout.",
    "Bar starts on the front delts, forearms vertical.",
], fedb="Standing_Military_Press")
E("seated-ohp", "Seated Barbell Press", "fire", "Strength", "Barbell + bench", [
    "Back tall against the pad; press straight up.",
    "Lower to the chin with control.",
], fedb="Seated_Barbell_Military_Press")
E("push-press", "Push Press", "fire", "Power", "Barbell", [
    "Short, vertical dip, then drive the bar with the legs.",
    "Punch the bar to lockout as the legs finish.",
], fedb="Push_Press")
E("power-jerk", "Power Jerk", "fire", "Olympic", "Barbell", [
    "Dip and drive, then punch yourself under in a quarter squat.",
    "Lockout and stabilize before you stand.",
], fedb="Power_Jerk")
E("split-jerk", "Split Jerk", "fire", "Olympic", "Barbell", [
    "Dip and drive straight up, then split fast under the bar.",
    "Front shin vertical, back knee soft; recover front foot first.",
], fedb="Split_Jerk")
E("db-shoulder-press", "Seated Dumbbell Press", "fire", "Hypertrophy", "Dumbbells", [
    "Elbows slightly forward; press in a smooth arc.",
    "Lower to ear level under control.",
], fedb="Dumbbell_Shoulder_Press")
E("standing-db-press", "Standing Dumbbell Press", "fire", "Strength", "Dumbbells", [
    "Squeeze the glutes; press without leaning back.",
    "Stack the wrists over the elbows.",
], fedb="Standing_Dumbbell_Press")
E("arnold-press", "Arnold Press", "fire", "Hypertrophy", "Dumbbells", [
    "Start palms in; rotate out as you press.",
    "Smooth rotation, no jerking.",
], fedb="Arnold_Dumbbell_Press")
E("single-arm-landmine", "Single-Arm Landmine Press", "fire", "Shoulder health", "Landmine", [
    "The arcing path is the shoulder-friendly press for overhead athletes.",
    "Reach through at the top and let the shoulder blade glide.",
], fedb="Single-Arm_Linear_Jammer")
E("landmine-push-press", "Landmine Push Press", "fire", "Power", "Landmine + handle", [
    "Dip and drive the bar up with the legs.",
    "Explode and lock out, then control back down.",
], fedb="Landmine_Linear_Jammer")
E("kb-push-press", "Single-Arm Kettlebell Push Press", "fire", "Power", "Kettlebell", [
    "Quick dip and drive; punch the bell to lockout.",
    "Wrist straight, bicep by the ear at the top.",
], fedb="One-Arm_Kettlebell_Push_Press")
E("lateral-raise", "Dumbbell Lateral Raise", "fire", "Hypertrophy", "Dumbbells", [
    "Lead with the elbows to shoulder height.",
    "Slight forward lean; pour the water out at the top.",
], fedb="Side_Lateral_Raise")
E("cable-lateral-raise", "Single-Arm Cable Lateral Raise", "fire", "Hypertrophy", "Cable", [
    "Cable behind you for tension at the bottom; raise to shoulder height.",
    "Slow negative and no shrug.",
], fedb="Standing_Low-Pulley_Deltoid_Raise")
E("lean-away-lateral", "Lean-Away Lateral Raise", "fire", "Hypertrophy", "Dumbbell", [
    "Hold the bench and lean away for a longer range.",
    "Raise smoothly and pause at the top.",
], fedb="One-Arm_Side_Laterals")
E("rear-delt-raise", "Seated Rear Delt Raise", "fire", "Shoulder health", "Dumbbells", [
    "Chest on the thighs; raise the dumbbells out wide.",
    "Pinkies up and squeeze the back of the shoulders.",
], fedb="Seated_Bent-Over_Rear_Delt_Raise")

# ---------------------------------------------------------------- FIRE: triceps
E("rope-pushdown", "Rope Pushdown", "fire", "Hypertrophy", "Cable + rope", [
    "Elbows pinned; split the rope at the bottom.",
    "Full lockout, then slow return.",
], fedb="Triceps_Pushdown_-_Rope_Attachment")
E("bar-pushdown", "Triceps Pushdown", "fire", "Hypertrophy", "Cable + bar", [
    "Lean slightly forward; elbows stay at your sides.",
    "Squeeze at lockout for one second.",
], fedb="Triceps_Pushdown")
E("overhead-cable-ext", "Overhead Cable Extension", "fire", "Hypertrophy", "Cable + rope", [
    "Elbows point forward; reach the rope overhead.",
    "Long-head stretch at the bottom is the money.",
], fedb="Cable_Rope_Overhead_Triceps_Extension")
E("db-overhead-ext", "Seated Dumbbell Overhead Extension", "fire", "Hypertrophy", "Dumbbell", [
    "Both hands under the top plate; elbows close to the head.",
    "Lower behind the head, extend fully.",
], fedb="Seated_Triceps_Press")
E("skull-crusher", "EZ-Bar Skull Crusher", "fire", "Hypertrophy", "EZ bar", [
    "Lower to the forehead or just behind; elbows still.",
    "Extend powerfully; don't let the elbows flare.",
], fedb="EZ-Bar_Skullcrusher")
E("jm-press", "JM Press", "fire", "Strength", "Barbell", [
    "Half skull crusher, half close-grip press; bar lowers toward the chin.",
    "Elbows stay forward; press back up powerfully.",
], fedb="JM_Press")
E("tate-press", "Tate Press", "fire", "Hypertrophy", "Dumbbells", [
    "Elbows flare out; lower the dumbbells to the chest.",
    "Extend up; pure triceps.",
], fedb="Tate_Press")
E("kickback", "Triceps Kickback", "fire", "Hypertrophy", "Dumbbell", [
    "Upper arm parallel to the floor; extend fully.",
    "Squeeze at the top for one second.",
], fedb="Tricep_Dumbbell_Kickback")
E("bench-dip", "Bench Dip", "fire", "Hypertrophy", "Bench", [
    "Hands on the bench behind you; lower to 90°.",
    "Shoulders stay down and back, away from the ears.",
], fedb="Bench_Dips")
E("single-arm-cable-ext", "Single-Arm Cable Extension", "fire", "Hypertrophy", "Cable", [
    "One arm at a time; lock out and squeeze.",
    "Keep the elbow fixed by your side.",
], fedb="Cable_One_Arm_Tricep_Extension")

# ---------------------------------------------------------------- core
E("hanging-leg-raise", "Hanging Leg Raise", "water", "Core", "Pull-up bar", [
    "No swinging; curl the pelvis up toward the bar.",
    "Lower slowly. The eccentric builds the abs.",
], fedb="Hanging_Leg_Raise")
E("ab-roller", "Ab Wheel Rollout", "water", "Core", "Ab wheel", [
    "Ribs down, glutes tight; roll out until you're about to lose it.",
    "Pull back with the abs, not the hips.",
], fedb="Ab_Roller")
E("dead-bug", "Dead Bug", "air", "Core", "Bodyweight", [
    "Low back pressed into the floor; extend opposite arm and leg.",
    "Exhale fully on each rep.",
], fedb="Dead_Bug")
E("plank", "Plank", "air", "Core", "Bodyweight", [
    "Squeeze the glutes and quads; push the floor away.",
    "Breathe. Shaking is just the body learning.",
], fedb="Plank")
E("cable-crunch", "Cable Crunch", "water", "Core", "Cable + rope", [
    "Hips still; crunch the ribs toward the pelvis.",
    "Round the spine; this isn't a hip hinge.",
], fedb="Cable_Crunch")
E("reverse-crunch", "Reverse Crunch", "water", "Core", "Bodyweight", [
    "Curl the hips off the floor; no momentum.",
    "Slow lower and keep the low back down.",
], fedb="Reverse_Crunch")

# ---------------------------------------------------------------- AIR: foam rolling (SMR)
E("foam-roll-quads", "Foam Roll: Quads", "air", "Recovery", "Foam roller", [
    "Slow passes, about an inch per second; pause on tender spots.",
    "Bend the knee on the sticky spots to dig deeper.",
], fedb="Quadriceps-SMR")
E("foam-roll-hamstrings", "Foam Roll: Hamstrings", "air", "Recovery", "Foam roller", [
    "Cross one leg over the other for more pressure.",
    "Breathe out on the tender spots and let them melt.",
], fedb="Hamstring-SMR")
E("foam-roll-calves", "Foam Roll: Calves", "air", "Recovery", "Foam roller", [
    "Stack the legs; rotate to find the inner and outer calf.",
    "Sand athletes' calves work overtime. Be generous here.",
], fedb="Calves-SMR")
E("foam-roll-it-band", "Foam Roll: Outer Thigh (IT Band)", "air", "Recovery", "Foam roller", [
    "Support with the top leg; roll from hip to just above the knee.",
    "Go gently. Spend more time on the glute and TFL above it.",
], fedb="Iliotibial_Tract-SMR")
E("foam-roll-glutes", "Foam Roll: Glutes & Piriformis", "air", "Recovery", "Foam roller", [
    "Sit on the roller, cross the ankle over the knee, lean into that hip.",
    "Small circles on the tender spots.",
], fedb="Piriformis-SMR")
E("foam-roll-adductors", "Foam Roll: Adductors", "air", "Recovery", "Foam roller", [
    "Face down, inner thigh on the roller; roll hip to knee.",
    "Pause and breathe on the knots.",
], fedb="Adductor")
E("foam-roll-lats", "Foam Roll: Lats", "air", "Recovery", "Foam roller", [
    "On your side, arm overhead; roll the armpit to mid-ribs.",
    "Rotate slightly forward and back to find the fibers.",
], fedb="Latissimus_Dorsi-SMR")
E("foam-roll-upper-back", "Foam Roll: Upper Back", "air", "Recovery", "Foam roller", [
    "Hug yourself to spread the shoulder blades; roll mid to upper back.",
    "Pause and extend over the roller to open the thoracic spine.",
], fedb="Rhomboids-SMR")
E("foam-roll-shins", "Shin Rolling (Massage Stick)", "air", "Recovery", "Massage stick", [
    "Seated, knee bent; roll the stick slowly up and down the front of the shin.",
    "Light pressure; the tibialis just needs a reset.",
], fedb="Anterior_Tibialis-SMR")
E("foam-roll-peroneals", "Foam Roll: Outer Calf (Peroneals)", "air", "Recovery", "Foam roller", [
    "Turn onto the outside of the lower leg and roll slowly.",
    "Sand ankles say thank you.",
], fedb="Peroneals-SMR")
E("foot-smr", "Foot Rolling (Ball)", "air", "Recovery", "Lacrosse / tennis ball", [
    "Roll the arch slowly from heel to toes.",
    "Pause and press into tender spots for 10 breaths.",
], fedb="Foot-SMR")
E("forearm-smr", "Foam Roll: Forearms", "air", "Recovery", "Foam roller", [
    "Roll the forearm and upper arm on the roller.",
    "Pass-and-set forearms deserve love too.",
], fedb="Brachialis-SMR")

# ---------------------------------------------------------------- AIR: mobility & stretching
E("worlds-greatest-stretch", "World's Greatest Stretch", "air", "Mobility", "Bodyweight", [
    "Lunge, elbow to instep, then rotate the arm to the sky.",
    "Breathe into each position; don't rush the rotation.",
], fedb="Worlds_Greatest_Stretch")
E("hip-circles", "Quadruped Hip Circles", "air", "Mobility", "Bodyweight", [
    "On all fours, draw the biggest circle you can with your knee.",
    "Keep the spine still; only the hip moves.",
], fedb="Hip_Circles_prone")
E("standing-hip-circles", "Standing Hip Circles", "air", "Mobility", "Bodyweight", [
    "Hands on the hips; make slow, big circles.",
    "Both directions; loosen the hips before you load them.",
], fedb="Standing_Hip_Circles")
E("knee-circles", "Knee Circles", "air", "Mobility", "Bodyweight", [
    "Feet together, hands on the knees; slow circles.",
    "Gentle warm-up for knees that jump all day.",
], fedb="Knee_Circles")
E("arm-circles", "Arm Circles", "air", "Mobility", "Bodyweight", [
    "Start small and grow bigger, forward then back.",
    "Relaxed shoulders, long arms.",
], fedb="Arm_Circles")
E("wrist-circles", "Wrist Circles", "air", "Mobility", "Bodyweight", [
    "Interlace the fingers and roll the wrists both ways.",
    "Your passing platform will thank you.",
], fedb="Wrist_Circles")
E("neck-stretch", "Side Neck Stretch", "air", "Mobility", "Bodyweight", [
    "Ear toward the shoulder; let the opposite shoulder sink.",
    "Breathe slowly, no pulling.",
], fedb="Side_Neck_Stretch")
E("cat-cow", "Cat-Cow", "air", "Mobility", "Bodyweight", [
    "Round up as you exhale, arch as you inhale.",
    "Move one vertebra at a time.",
], fedb="Cat_Stretch")
E("childs-pose", "Child's Pose", "air", "Mobility", "Bodyweight", [
    "Knees wide, hips to the heels, arms long.",
    "Breathe into the back of the ribs.",
], fedb="Childs_Pose")
E("inchworm", "Inchworm", "air", "Mobility", "Bodyweight", [
    "Walk the hands out to a plank, then the feet to the hands.",
    "Keep the legs as straight as you can.",
], fedb="Inchworm")
E("runners-stretch", "Runner's Stretch", "air", "Mobility", "Bodyweight", [
    "Staggered stance, hands beside the front foot, front heel flat.",
    "Push the hips up and back; feel the front hamstring and back calf.",
], fedb="Runners_Stretch")
E("kneeling-hip-flexor", "Half-Kneeling Hip Flexor Stretch", "air", "Mobility", "Bodyweight", [
    "Tuck the pelvis and squeeze the back glute, then shift forward.",
    "Reach the arm overhead to add the lats.",
], fedb="Kneeling_Hip_Flexor")
E("straddle", "Straddle Stretch", "air", "Mobility", "Bodyweight", [
    "Legs wide, toes up; walk the hands forward.",
    "Long spine first, then fold.",
], fedb="The_Straddle")
E("seated-forward-fold", "Seated Hamstring Stretch", "air", "Mobility", "Bodyweight", [
    "Hinge from the hips and reach for the toes.",
    "Soft knees are fine; chase length, not pain.",
], fedb="Seated_Floor_Hamstring_Stretch")
E("90-90-hamstring", "90/90 Hamstring Stretch", "air", "Mobility", "Bodyweight", [
    "On your back, thigh vertical; slowly straighten the knee.",
    "Keep the other leg relaxed; pulse gently.",
], fedb="90_90_Hamstring")
E("side-quad-stretch", "Side-Lying Quad Stretch", "air", "Mobility", "Bodyweight", [
    "Pull the heel to the glute and push the hip forward.",
    "Knees stay together.",
], fedb="On_Your_Side_Quad_Stretch")
E("figure-four", "Figure-Four Stretch", "air", "Mobility", "Bodyweight", [
    "Ankle over the knee; draw the legs toward you.",
    "Relax the jaw. Glutes release when you do.",
], fedb="Ankle_On_The_Knee")
E("knee-across", "Supine Twist", "air", "Mobility", "Bodyweight", [
    "Knee across the body, shoulders flat; look away.",
    "Let gravity do it; exhale deeper each breath.",
], fedb="Knee_Across_The_Body")
E("hug-knees", "Knees to Chest", "air", "Mobility", "Bodyweight", [
    "Hug both knees and rock gently side to side.",
    "Low back melts into the floor.",
], fedb="Hug_Knees_To_Chest")
E("groin-stretch", "Butterfly Groin Stretch", "air", "Mobility", "Bodyweight", [
    "Soles together; fold forward with a long spine.",
    "Elbows gently press the knees toward the floor.",
], fedb="Groin_and_Back_Stretch")
E("dowel-pass-through", "Dowel Shoulder Pass-Through", "air", "Mobility", "PVC / broomstick", [
    "Wide grip; arc the stick overhead and behind with straight arms.",
    "Narrow the grip a little each week.",
], fedb="Round_The_World_Shoulder_Stretch")
E("cross-body-stretch", "Cross-Body Shoulder Stretch", "air", "Mobility", "Bodyweight", [
    "Pull the arm across the chest below shoulder height.",
    "Keep the shoulder blade down; gentle stretch.",
], fedb="Shoulder_Stretch")
E("pec-stretch", "Stick Chest & Shoulder Stretch", "air", "Mobility", "Dowel / broomstick", [
    "Wide grip on a stick, then lift it slowly up and back behind your head.",
    "Stop where the chest opens; breathe into the front of the shoulders.",
], fedb="Chest_And_Front_Of_Shoulder_Stretch")
E("lat-stretch-wall", "Wall Lat Stretch", "air", "Mobility", "Wall", [
    "Forearm on the wall; lean in and sink the chest.",
    "Feel the stretch from armpit to hip.",
], fedb="One_Arm_Against_Wall")
E("upper-back-stretch", "Upper Back Stretch", "air", "Mobility", "Bodyweight", [
    "Clasp the hands in front and round the upper back.",
    "Push the hands away to spread the shoulder blades.",
], fedb="Upper_Back_Stretch")
E("triceps-stretch", "Overhead Triceps Stretch", "air", "Mobility", "Bodyweight", [
    "Reach down the back, other hand gently pushes the elbow.",
    "Stay tall; don't crunch the neck.",
], fedb="Triceps_Stretch")
E("forearm-stretch", "Kneeling Forearm Stretch", "air", "Mobility", "Bodyweight", [
    "Fingers point toward the knees; lean back gently.",
    "Hitting arms and passing platforms need this.",
], fedb="Kneeling_Forearm_Stretch")
E("seated-twist", "Seated Spinal Twist", "air", "Mobility", "Bodyweight", [
    "Cross a leg, sit tall, then rotate toward the bent knee.",
    "Lengthen on the inhale, twist on the exhale.",
], fedb="Dancers_Stretch")
E("prone-scorpion", "Prone Scorpion", "air", "Mobility", "Bodyweight", [
    "Face down, arms out; swing the heel across toward the opposite hand.",
    "Gentle and controlled. Wake up the hips and T-spine.",
], fedb="Iron_Crosses_stretch")
E("calf-stretch", "Wall Calf Stretch", "air", "Mobility", "Wall", [
    "Back heel down, knee straight; lean into the wall.",
    "Hold, then bend the knee slightly to find the soleus.",
], fedb="Calf_Stretch_Hands_Against_Wall")
E("soleus-stretch", "Soleus & Achilles Stretch", "air", "Mobility", "Bodyweight", [
    "Bent knee, heel down; sink the knee over the toes.",
    "Long, slow breaths. Achilles health equals jump health.",
], fedb="Standing_Soleus_And_Achilles_Stretch")
E("pelvic-tilt-bridge", "Pelvic Tilt into Bridge", "air", "Mobility", "Bodyweight", [
    "Tilt the pelvis, then peel the spine up one segment at a time.",
    "Lower the same way, one vertebra at a time.",
], fedb="Pelvic_Tilt_Into_Bridge")

# --- yoga & mobility drills without an exact DB photo (searched, else placeholder)
E("downward-dog", "Downward Dog", "air", "Yoga", "Mat", [
    "Hips high, push the floor away; heels reach down.",
    "Pedal the feet to wake up the calves.",
], pict="yoga", search="downward facing dog yoga",
  desc="From hands and knees, lift the hips up and back into an inverted V.")
E("cobra", "Cobra Pose", "air", "Yoga", "Mat", [
    "Hips down, press the chest forward and up.",
    "Shoulders away from the ears; gentle back bend.",
], pict="yoga", search="cobra pose yoga",
  desc="Lying face down, press through the hands to lift the chest while hips stay on the floor.")
E("low-lunge", "Low Lunge (Crescent)", "air", "Yoga", "Mat", [
    "Back knee down; sink the hips forward and reach up.",
    "Squeeze the back glute to deepen the hip-flexor stretch.",
], pict="lunge", search="low lunge anjaneyasana yoga",
  desc="Kneeling lunge with arms overhead. Sink the hips forward to open the front of the back hip.")
E("warrior-two", "Warrior II", "air", "Yoga", "Mat", [
    "Front knee over the ankle, arms long, gaze past the front hand.",
    "Sink and hold. The legs burn, the mind stays calm.",
], pict="yoga", search="warrior II yoga pose",
  desc="Wide stance with the front knee bent and arms extended to the sides.")
E("triangle-pose", "Triangle Pose", "air", "Yoga", "Mat", [
    "Long legs; hinge sideways and reach the top arm to the sky.",
    "Stack the shoulders and breathe into the side body.",
], pict="yoga", search="triangle pose trikonasana",
  desc="Straight-legged wide stance, hinge sideways over the front leg with arms in one vertical line.")
E("pigeon-pose", "Pigeon Pose", "air", "Yoga", "Mat", [
    "Front shin angled forward, back leg long; square the hips.",
    "Fold forward slowly and breathe into the outer hip.",
], pict="stretchfloor", search="pigeon pose yoga",
  desc="From all fours, bring one knee forward behind the wrist and extend the other leg back. Fold over the front shin.")
E("happy-baby", "Happy Baby", "air", "Yoga", "Mat", [
    "Hold the outside of the feet, knees toward the armpits.",
    "Rock gently; tailbone stays heavy.",
], pict="stretchfloor", search="happy baby pose yoga",
  desc="On your back, hold the feet with the knees bent wide toward the armpits.")
E("legs-up-wall", "Legs Up the Wall", "air", "Recovery", "Wall", [
    "Hips close to the wall, legs resting up; arms relaxed.",
    "Slow nasal breathing; let the legs drain.",
], pict="stretchfloor", search="legs up the wall pose",
  desc="Lie on your back with your legs resting vertically against a wall.")
E("90-90-switch", "90/90 Hip Switch", "air", "Mobility", "Bodyweight", [
    "Sit tall with both knees at 90°; rotate the knees side to side.",
    "Hands-free if you can, and lead with the hips.",
], pict="stretchfloor", search="90 90 hip stretch",
  desc="Seated with both legs bent at 90° (front leg and back leg), rotate the knees to switch sides without using your hands.")
E("thread-needle", "Thread the Needle", "air", "Mobility", "Bodyweight", [
    "From all fours, slide one arm under the body and rest the shoulder down.",
    "Then reach to the sky. The T-spine loves rotation.",
], pict="stretchfloor", search="thread the needle stretch",
  desc="On hands and knees, thread one arm under the opposite arm, rotating the upper back, then open to the ceiling.")
E("open-book", "Open Book Rotation", "air", "Mobility", "Bodyweight", [
    "Side-lying, knees stacked; open the top arm like a book.",
    "Follow the hand with your eyes; exhale as you open.",
], pict="stretchfloor",
  desc="Lie on your side with the knees bent and stacked. Rotate the top arm open across the body to the floor behind you.")
E("sleeper-stretch", "Sleeper Stretch", "air", "Shoulder health", "Bodyweight", [
    "Lying on the shoulder, gently press the forearm toward the floor.",
    "Mild stretch only. The hitting arm needs internal rotation back.",
], pict="stretchfloor",
  desc="Lie on your side with the bottom arm in front at 90°. Gently press the forearm down to stretch the back of the shoulder.")
E("wall-slide", "Wall Slide", "air", "Shoulder health", "Wall", [
    "Back and forearms on the wall; slide up while keeping contact.",
    "Ribs down; feel the lower traps and serratus.",
], pict="stand",
  desc="Stand with your back to a wall, arms in a goalpost position, and slide the arms overhead while keeping contact.")
E("leg-swings", "Leg Swings", "air", "Mobility", "Bodyweight", [
    "Hold a post; swing front-to-back, then side-to-side.",
    "Gradually bigger, stay tall and relaxed.",
], pict="stand",
  desc="Hold a support and swing one leg forward and back, then across the body and out to the side.")
E("bird-dog", "Bird Dog", "air", "Core", "Bodyweight", [
    "Reach the opposite arm and leg long; hips stay level.",
    "Pause and exhale. Balance a cup of tea on the low back.",
], pict="crawl", search="bird dog exercise",
  desc="On hands and knees, extend the opposite arm and leg, pause, and return with control.")
E("box-breathing", "Box Breathing", "air", "Recovery", "None", [
    "Inhale 4, hold 4, exhale 4, hold 4.",
    "Shoulders heavy, jaw loose. Breath is the root of all bending.",
], pict="breathe", search="meditation breathing seated",
  desc="Seated or lying, breathe in a square: inhale for 4 seconds, hold 4, exhale 4, hold 4.")
E("easy-swim", "Easy Swim", "air", "Recovery", "Pool", [
    "Long, relaxed strokes; easy enough to smile.",
    "Mix in backstroke to open the chest and shoulders.",
], pict="swim", search="freestyle swimming pool",
  desc="Continuous easy swimming. Light, conversational effort that flushes the shoulders and legs.")
E("sand-footwork", "Sand Footwork Flow", "air", "Recovery", "Sand", [
    "Light shuffles, crossovers and skips at walking intensity.",
    "Quiet feet, loose arms. Practice, not punishment.",
], pict="shuffle",
  desc="Low-intensity volleyball footwork patterns on sand: shuffles, crossover steps, drop steps and skips.")
E("bike-easy", "Easy Stationary Bike", "air", "Recovery", "Bike", [
    "Zone 1 easy, enough to hold a conversation.",
    "High cadence, low resistance; legs flush, mind clears.",
], fedb="Bicycling_Stationary")
E("row-easy", "Easy Row (Erg)", "air", "Warm-up", "Rowing machine", [
    "Legs, hips, then arms. Smooth, relaxed strokes.",
    "Breathe and let your heart rate rise gradually.",
], fedb="Rowing_Stationary")
E("incline-walk", "Incline Treadmill Walk", "air", "Recovery", "Treadmill", [
    "Moderate incline, easy pace; no holding the rails.",
    "Nasal breathing only. That's the speed limit.",
], fedb="Walking_Treadmill")
