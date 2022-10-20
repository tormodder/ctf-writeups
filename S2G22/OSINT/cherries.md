I completely forgot to save the task and picture for this writeup. But essentially we're given the cherries.png image and told the locaiton is in the Vestre Aker District of Oslo, and to find the building number of the house on the right.

![alt text](https://github.com/tormodder/ctf/tree/main/S2G22/OSINT/cherries.png?raw=true)


After some failed attempts at trying to Google lens both houses, hoping they had been involved in some public news story in the past, I realized the best way to solve the challenge was to simply deduce where it could be and use google street view. 

For this it turned out a past job as a delivery driver in northern Oslo would come in handy. Vestre Aker has some distinguishing geographical features. Namely, the large Holmenkollen ski jump in the north, and the fact that very many houses have a view of the fjord and the city centre. In the picture it looks like our house has neither, so at the very least it cannot be in the northern part of Vestre Aker.

In addition I thought I saw the top of a block building in the background. This is also not very typical of Vestre Aker, where there are a lot of individual houses. Looking back now I think my assumption that the building in the background was a block is wrong, but it's a wrong assumption that led me to a right conculsion, so whatever.

I still hadn't narrowed it down very much though, and spent quite a bit of time aimlessly walking around in google street view. That's until I tried to query "Vestre Aker Bydel" to see the borders of the district, but instead got a picture of the district centre at Røa - and there were several blocks there! So I assumed the buildings in the background must be part of Røa. Again, this turned out to be a wrong assumption, because even if the building in the background was a block, you're not facing Røa in the picture.

Anyway, having earlier ruled out that the view had to be towards the north, since I would probably see the ski jump or at least the large hill it's positioned on if that were the case, I figured the location had to be north of Røa, but close. This turned out to be true. I placed the marker arbitrarily on Sørkedalsveien, the main road leading north from Røa. Turns out I got immensely lucky, and didn't have to walk long until I came upon the house - Sørkedalsveien 217

I still wasn't done though, since the challenge asked for the building number, not the address. This would turn out to be the easiest part of the challenge. I just googled how to find building numbers, input the address on "https://seeiendom.kartverket.no/" and got the number: 80063954.
