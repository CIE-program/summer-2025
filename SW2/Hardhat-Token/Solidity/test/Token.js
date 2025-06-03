const { expect } = require("chai");

describe("Token contract", function () {
  it("Deployment should assign the total supply of tokens to the owner", async function () {
    const [owner] = await ethers.getSigners();

    const hardhatToken = await ethers.deployContract("Token");

    const ownerBalance = await hardhatToken.balanceOf(owner.address);
    expect(await hardhatToken.totalSupply()).to.equal(ownerBalance);
  });

  it("Should Transfer Tokens from One Account to Another Account", async function() {
    const [owner, first, second] = await ethers.getSigners();
    const hardhatToken = await ethers.deployContract("Token");

    await hardhatToken.transfer(first.address, 100);
    expect(await hardhatToken.balanceOf(first.address)).to.equal(100);
  }
)
});