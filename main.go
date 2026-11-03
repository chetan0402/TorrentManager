package main

import (
	"cmp"
	"encoding/json/v2"
	"net/http"
	"slices"

	spotraygo "github.com/chetan0402/SpotRay-go"
)

const baseURL = "http://127.0.0.1:8080/api/v2"

const torrentInfoURL = baseURL + "/torrents/info"

const FONT = "RobotoMonoNerdFont-Medium.ttf"

type Torrent struct {
	Hash                string  `json:"hash"`
	Name                string  `json:"name"`
	ActiveTime          int     `json:"active_time"`
	SeedRatio           float32 `json:"seed_ratio"`
	SavePath            string  `json:"save_path"`
	MaxInactiveSeedTime int     `json:"max_inactive_seed_time"`
	MaxRatio            int     `json:"max_ratio"`
	MaxSeedingTime      int     `json:"max_seeding_time"`
	eta                 int     // in seconds
}

func getTorrents() []Torrent {
	resp, err := http.Get(torrentInfoURL)
	if err != nil {
		panic(err)
	}
	var torrents []Torrent
	if err := json.UnmarshalRead(resp.Body, &torrents); err != nil {
		panic(err)
	}
	for i, v := range torrents {
		torrents[i].eta = int((float32(v.ActiveTime) / (v.SeedRatio + 1e-9)) * (1 - v.SeedRatio))
	}
	return torrents
}

func getMainState(sortByActiveTime bool) *spotraygo.State {
	torrents := getTorrents()
	if sortByActiveTime {
		slices.SortFunc(torrents, func(a, b Torrent) int {
			return cmp.Compare(a.ActiveTime, b.ActiveTime)
		})
	} else {
		slices.SortFunc(torrents, func(a, b Torrent) int {
			return cmp.Compare(a.eta, b.eta)
		})
	}
	opts := make([]spotraygo.Item, len(torrents))
	for i := range opts {
		opts[i].Key = torrents[i].Hash
		opts[i].Value = torrents[i].Name
	}
	return &spotraygo.State{
		Options:  opts,
		Keybinds: map[int32]func(*spotraygo.App){},
		Font:     FONT,
	}
}

func main() {
	app := spotraygo.NewApp()
	app.SetState(getMainState(true))
	app.Start()
}
