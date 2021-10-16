A pretty rough autorigger that I made a few months ago, in about two weeks.
Still missing components, and is far from production ready, but I wanted to get it up online, and get back into working on it.

I will be doing all my small commits to the $Staging branch, so check there if $Master feels like it hasn't been updated for a while!

I can't promise that anything in $Staging will work, as for the meanwhile it'll mostly be some pretty big changes to the codebase


## USAGE
### ! This autorigger currently is intended to be used entirely through code, so no UI exists for it, though that is planned for the next update !

For each character rig you want to create, you'll want to make a new copy of `Template_Run_Script.py`, with the character name as the file name.

You can then edit this file to create all the individual pieces for that specific character, based on the build components in `Build_Components.py`

Finally you can run the individual character's build script from inside the rig file to build the rig on top of an already existing joint hierarchy

## Example rig

Contains ribbon based spine, FKIK arms with space switching, full hand rig, digitgrade legs, and other parts
![image](https://user-images.githubusercontent.com/37246948/135916298-46022efe-c81f-4022-a0cb-d90006d67175.png)


## Future Version plans
v.2: Create a "Basic" UI, that keeps the modularity of the current setup, while also being significantly easier to use for anyone who can't, or doesn't want to, use code to create rigs.

v.3: Reformat some parts of the code to be more modular, like splitting FKIK creation, and Space Switching for limbs out to their own functions.

v.4 and further: Unknown as of yet.