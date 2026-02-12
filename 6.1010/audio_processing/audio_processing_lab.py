"""
6.101 Lab:
Audio Processing
"""

import wave
import struct

# No additional imports allowed!


def backwards(sound):
    """
    Returns a new sound containing the samples of the original in reverse
    order, without modifying the input sound.

    Args:
        sound: a dictionary representing the original mono sound

    Returns:
        A new mono sound dictionary with the samples in reversed order
    """
    backward_sound = {}
    backward_sound["rate"] = sound["rate"]
    backward_sound["samples"] = sound["samples"][::-1]
    return backward_sound
    raise NotImplementedError


def mix(sound1, sound2, p):
    """
    Returns a new sound containing a mix of two original samples.

    Args:
        sound1: a dictionary representing one original mono sound
        sound2: a second dictionary representing another original mono sound
        p: a float between 0 and 1 (inclusive). The returned mixed sound will
        take p times the samples in sound1 and 1-p times the samples in sound2

    Returns:
        IF sound1 and sound2 both have designated rates AND those rates are equal:
        returns mixture of sound1 and sound2 as dictated by p. The
        mix will be as long as the shorter sound.
        ELSE: returns none
    """
    try:  # check if "rate" exists in both files and if said "rate"s are equal
        if sound1["rate"] != sound2["rate"]:
            return None
    except KeyError:
        return None

    rate = sound1["rate"]  # get rate
    sound1 = sound1["samples"]
    sound2 = sound2["samples"]
    if len(sound1) < len(sound2):  # identify shorter clip
        mix_len = len(sound1)
    elif len(sound2) < len(sound1):
        mix_len = len(sound2)
    else:
        mix_len = len(sound1)

    mix_sound = []
    for i in range(0, mix_len):
        s2, s1 = p * sound1[i], sound2[i] * (1 - p)
        mix_sound.append(s1 + s2)  # add sounds

    return {"rate": rate, "samples": mix_sound}  # return new sound


def echo(sound, num_echoes, delay, scale):
    """
    Compute a new signal consisting of several scaled-down and delayed versions
    of the input sound. Does not modify input sound.

    Args:
        sound: a dictionary representing the original mono sound
        num_echoes: int, the number of additional copies of the sound to add
        delay: float, the amount of seconds each echo should be delayed
        scale: float, the amount by which each echo's samples should be scaled

    Returns:
        A new mono sound dictionary resulting from applying the echo effect.
    """

    sample_delay = round(sound["rate"] * delay)

    sound_echo = {}
    sound_echo["rate"] = sound["rate"]
    sound_echo["samples"] = [0] * (
        len(sound["samples"]) + sample_delay * num_echoes
    )  # creating a list of correct length

    for i in range(
        len(sound["samples"])
    ):  # adding the original samples to the new list
        sound_echo["samples"][i] = sound["samples"][i]

    for echo_iter in range(num_echoes):
        current = (
            echo_iter + 1
        ) * sample_delay  # keeping track of starting point for new echo
        scale_count = scale ** (echo_iter + 1)

        for sound_iter in range(len(sound["samples"])):
            sound_echo["samples"][current + sound_iter] += (
                scale_count * sound["samples"][sound_iter]
            )

    return sound_echo

    raise NotImplementedError


def pan(sound):
    """
    Scale stereo sound such that left channel begins at full volume but
    decreases to zero, whereas right channel begins at zero and increases to
    full volume

    Args:
        sound: a stereo sound consisting of a dictionary with three key/value pairs:
            "rate": the sampling rate (as an int), in units of samples per second
            "left": a list containing samples for the left speaker
            "right": a list containing samples for the right speaker

    Returns:
        let N be the number of samples in a sound
        returns "panned" version of the original sound in which we scale
        the first sample in the left channel by 1, then 1 - 1/(N-1), then 1 - 2/(N-1)...
        ending at 0 and the second sample in the left channel by 0, then 1 - (N-2)/(N-1)...
        ending at 1.
    """
    panned_sound = {}  # duplicating the original sound
    panned_sound["rate"] = sound["rate"]
    panned_sound["left"] = sound["left"][:]
    panned_sound["right"] = sound["right"][:]

    N = (
        len(panned_sound["left"]) - 1
    )  # setting N - for simplicity, N is actually set to N - 1 as defined in docstring

    scale_list = [0]  # initializing list of scaling factors
    for i in range(N):
        scale_list.append((i + 1) / N)

    for right_mod in range(
        len(panned_sound["right"])
    ):  # applying scales to right channel
        panned_sound["right"][right_mod] = (
            panned_sound["right"][right_mod] * scale_list[right_mod]
        )

    scale_list.reverse()  # reversing order of scales

    for left_mod in range(len(panned_sound["left"])):  # applying scales to left channel
        panned_sound["left"][left_mod] = (
            panned_sound["left"][left_mod] * scale_list[left_mod]
        )

    return panned_sound

    raise NotImplementedError


def remove_vocals(sound):
    """
    Remove the vocals from a stereo sound by subtracting the right and left channels,
    resulting in a mono sound

    Args:
        sound: a stereo sound

    Returns:
        a mono sound whose sample list contains the difference between the left
        and right channels of the original sound
    """
    removed = {}
    removed["rate"] = sound["rate"]
    removed["samples"] = sound["left"][:]

    for i in range(len(removed["samples"])):
        removed["samples"][i] -= sound["right"][i]

    return removed

    raise NotImplementedError


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def load_wav(filename, stereo=False):
    """
    Load a file and return a sound dictionary.

    Args:
        filename: string ending in '.wav' representing the sound file
        stereo: bool, by default sound is loaded as mono, if True sound will
            have left and right stereo channels.

    Returns:
        A dictionary representing that sound.
    """
    sound_file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = sound_file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    left = []
    right = []
    for i in range(count):
        frame = sound_file.readframes(1)
        if chan == 2:
            left.append(struct.unpack("<h", frame[:2])[0])
            right.append(struct.unpack("<h", frame[2:])[0])
        else:
            datum = struct.unpack("<h", frame)[0]
            left.append(datum)
            right.append(datum)

    if stereo:
        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = [(ls + rs) / 2 for ls, rs in zip(left, right)]
        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Save sound to filename location in a WAV format.

    Args:
        sound: a mono or stereo sound dictionary
        filename: a string ending in .WAV representing the file location to
            save the sound in
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for l_val, r_val in zip(sound["left"], sound["right"]):
            l_val = int(max(-1, min(1, l_val)) * (2**15 - 1))
            r_val = int(max(-1, min(1, r_val)) * (2**15 - 1))
            out.append(l_val)
            out.append(r_val)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # Code placed inside the if __name__ == "__main__" statement will only
    # be executed when you run the lab.py file.

    # Code placed in this special if statement will not be executed when you run
    # the tests in the test.py file or when you submit your code to the submission
    # server.

    # This makes it a good place to put your code for generating and saving
    # sounds, or any other code you write for testing on your computer.

    # Note that your checkoff conversation with a staff member will likely involve
    # showing and discussing the code you wrote to generate the sounds that you
    # submitted on the lab page, so please do not delete that code. However, you
    # can comment it out.

    # Here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file):

    # print("Loading hello file...")
    # hello = load_wav("sounds/hello.wav")
    # write_wav(backwards(hello), "hello_reversed.wav")

    # print("Loading mystery file...")
    # mystery = load_wav("sounds/mystery.wav")
    # write_wav(backwards(mystery), "mystery_reversed.wav")

    # print("Loading synth file...")
    # print("Loading water file...")
    # synth = load_wav("sounds/synth.wav")
    # water = load_wav("sounds/water.wav")
    # write_wav(mix(synth, water, 0.2), "synth_water_mix.wav")

    # print("Loading chord file...")
    # chord = load_wav("sounds/chord.wav")
    # write_wav(echo(chord, 5, 0.3, 0.6), "chord_echo.wav")

    # print("Loading car file...")
    # car = load_wav("sounds/car.wav", stereo = True)
    # write_wav(pan(car), "car_panned.wav")

    print("Loading lookout mountain file...")
    lookout_mountain = load_wav("sounds/lookout_mountain.wav", stereo=True)
    write_wav(remove_vocals(lookout_mountain), "lookout_mountain_vocals_removed.wav")
