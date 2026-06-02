MMD := $(wildcard mmd/*.mmd)
PNG := $(patsubst mmd/%.mmd,png/%.png,$(MMD))

all: $(PNG)

png/%.png: mmd/%.mmd
	mkdir -p $(dir $@)
	mmdc -i $< -o $@
